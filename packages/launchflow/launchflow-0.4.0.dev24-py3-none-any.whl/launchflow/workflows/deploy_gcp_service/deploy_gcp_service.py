import asyncio
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from docker.errors import BuildError

from launchflow import exceptions
from launchflow.config import config
from launchflow.flows.flow_logger import WorkflowProgress
from launchflow.gcp.cloud_run import CloudRun
from launchflow.workflows.commands.tf_commands import TFApplyCommand, TFImportCommand
from launchflow.workflows.deploy_gcp_service.schemas import (
    DeployCloudRunInputs,
    DeployGCPServiceOutputs,
    PromoteCloudRunInputs,
)
from launchflow.workflows.utils import run_tofu, tar_source_in_memory


async def _upload_source_tarball_to_gcs(
    source_tarball_gcs_path: str,
    artifact_bucket: str,
    local_source_dir: str,
    workflow_progress: WorkflowProgress,
    build_ignore: List[str],
):
    try:
        from google.cloud import storage
    except ImportError:
        raise exceptions.MissingGCPDependency()

    with workflow_progress.step(
        "Uploading source tarball to GCS", "Source tarball uploaded"
    ):

        def upload_async():
            source_tarball = tar_source_in_memory(local_source_dir, build_ignore)

            try:
                bucket = storage.Client().get_bucket(artifact_bucket)
                blob = bucket.blob(source_tarball_gcs_path)
                blob.upload_from_file(source_tarball)
            except Exception:
                raise exceptions.UploadSrcTarballFailed()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, upload_async)


async def _apply_docker_repository_tf(
    tf_backend_prefix: str,
    gcp_project_id: str,
    gcp_default_region: str,
    service_name: str,
    logs_file: str,
    workflow_progress: WorkflowProgress,
    launchflow_state_url: str,
) -> str:
    with workflow_progress.step(
        "Setting up Docker repository", "Docker repository ready"
    ):
        docker_repo_tf_apply_command = TFApplyCommand(
            tf_module_dir="workflows/tf/docker/gcp_artifact_registry",
            backend=config.launchflow_yaml.backend,
            # TODO: move this under the service name dir
            tf_state_prefix=tf_backend_prefix,
            tf_vars={
                "gcp_project_id": gcp_project_id,
                "gcp_region": gcp_default_region,
                "repository_name": service_name,
            },
            logs_file=logs_file,
            launchflow_state_url=launchflow_state_url,
        )
        docker_repo_tf_outputs: Dict[str, Any] = await run_tofu(
            docker_repo_tf_apply_command
        )
        docker_repository: Optional[str] = docker_repo_tf_outputs.get(
            "docker_repository"
        )
        if docker_repository is None:
            raise ValueError("Docker repository not found in tf outputs")

    return docker_repository


# TODO: builds are not going to the correct gcp project
async def _run_docker_gcp_cloud_build(
    docker_repository: str,
    docker_image_name: str,
    docker_image_tag: str,
    gcs_source_bucket: str,
    gcs_source_object: str,
    gcp_project_id: str,
    dockerfile_path: str,
    artifact_bucket: str,
    workflow_progress: WorkflowProgress,
):
    try:
        from google.cloud.devtools import cloudbuild_v1
    except ImportError:
        raise exceptions.MissingGCPDependency()

    with workflow_progress.step("Building Docker image", "Docker image built"):
        latest_image_name = f"{docker_repository}/{docker_image_name}:latest"
        tagged_image_name = (
            f"{docker_repository}/{docker_image_name}:{docker_image_tag}"
        )

        # Create the Cloud Build build plan
        build = cloudbuild_v1.Build(
            source=cloudbuild_v1.Source(
                storage_source=cloudbuild_v1.StorageSource(
                    bucket=gcs_source_bucket, object_=gcs_source_object
                )
            ),
            # TODO: determine if we should set the service account still
            # service_account=f"projects/{gcp_project_id}/serviceAccounts/{env_service_account_email}",
            logs_bucket=f"gs://{artifact_bucket}/logs/cloud-builds",
            steps=[
                # Pull the latest image from the registry to use as a cache
                cloudbuild_v1.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    entrypoint="bash",
                    args=[
                        "-c",
                        f"docker pull {latest_image_name} || exit 0",
                    ],
                ),
                # Build the docker image with the cache from the latest image
                cloudbuild_v1.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    args=[
                        "build",
                        "-t",
                        latest_image_name,
                        "-t",
                        tagged_image_name,
                        "--cache-from",
                        latest_image_name,
                        "-f",
                        dockerfile_path,
                        ".",
                    ],
                ),
            ],
            # NOTE: This is what pushes the image to the registry
            images=[latest_image_name, tagged_image_name],
        )
        # Submit the build to Cloud Build
        cloud_build_client = cloudbuild_v1.CloudBuildAsyncClient()
        operation = await cloud_build_client.create_build(
            project_id=gcp_project_id, build=build
        )
        build_url = f"https://console.cloud.google.com/cloud-build/builds/{operation.metadata.build.id}?project={gcp_project_id}"
        # Add logs to the table to the table
        workflow_progress.add_logs_row("build", build_url)
        await operation.result()

    # Return the docker image name
    return tagged_image_name


def _write_build_logs(file_path: str, log_stream, workflow_progress: WorkflowProgress):
    with open(file_path, "w") as f:
        for chunk in log_stream:
            if "stream" in chunk:
                f.write(chunk["stream"])
    # NOTE: we don't add the logs to the progress until after because the file doesn't exist yet
    workflow_progress.add_logs_row("build", file_path)


# TODO: Look into cleaning up old images. I noticed my docker images were taking up a lot of space
# after running this workflow multiple times
async def _build_docker_image_local(
    docker_repository: str,
    docker_image_name: str,
    docker_image_tag: str,
    local_source_dir: str,
    dockerfile_path: str,
    workflow_progress: WorkflowProgress,
    build_logs: str,
):
    try:
        from docker import errors, from_env
    except ImportError:
        raise exceptions.MissingDockerDependency()
    try:
        import google.auth
        import google.auth.transport.requests

    except ImportError:
        raise exceptions.MissingGCPDependency()

    with workflow_progress.step("Building Docker image", "Docker image built"):
        docker_client = from_env()
        latest_image_name = f"{docker_repository}/{docker_image_name}:latest"
        tagged_image_name = (
            f"{docker_repository}/{docker_image_name}:{docker_image_tag}"
        )
        # Authenticate with the docker registry
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        creds.refresh(google.auth.transport.requests.Request())
        docker_client.login(
            username="oauth2accesstoken",
            password=creds.token,
            registry=f"https://{docker_repository.split('/')[0]}",
        )

        # Pull the latest image from the registry to use as a cache
        try:
            # TODO: This is throwing a 500 error saying unauthorized
            docker_client.images.pull(latest_image_name)
            cache_from = [latest_image_name]
        except errors.NotFound:
            # NOTE: this happens on the first build
            cache_from = []

        # Build the docker image with the cache from the latest image
        loop = asyncio.get_event_loop()
        try:
            _, log_stream = await loop.run_in_executor(
                None,
                lambda: docker_client.images.build(
                    path=os.path.dirname(local_source_dir),
                    dockerfile=dockerfile_path,
                    tag=tagged_image_name,
                    cache_from=cache_from,
                    # NOTE: this is required to build on mac
                    platform="linux/amd64",
                ),
            )
            _write_build_logs(build_logs, log_stream, workflow_progress)
        except BuildError as e:
            _write_build_logs(build_logs, e.build_log, workflow_progress)
            raise

        # Tag as latest
        docker_client.images.get(tagged_image_name).tag(latest_image_name)

        # Push the images to the registry
        docker_client.images.push(tagged_image_name)
        docker_client.images.push(latest_image_name)

    # Return the docker image name
    return tagged_image_name


async def _promote_docker_image(
    source_env_region: str,
    source_docker_image: str,
    target_docker_repository: str,
    docker_image_name: str,
    docker_image_tag: str,
    target_gcp_project_id: str,
    target_artifact_bucket: str,
    workflow_progress: WorkflowProgress,
):
    try:
        import google.auth
        import google.auth.transport.requests
        from google.cloud.devtools import cloudbuild_v1
    except ImportError:
        raise exceptions.MissingGCPDependency()

    with workflow_progress.step("Promoting Docker image", "Docker image promoted"):
        target_image = f"{target_docker_repository}/{docker_image_name}"
        tagged_target_image = f"{target_image}:{docker_image_tag}"

        # Fetch creds to use for pulling the source image in the target's project
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        creds.refresh(google.auth.transport.requests.Request())

        build = cloudbuild_v1.Build(
            # TODO: determine if we should set the service account still
            # service_account=f"projects/{target_gcp_project_id}/serviceAccounts/{target_env_service_account_email}",
            logs_bucket=f"gs://{target_artifact_bucket}/logs/cloud-builds",
            steps=[
                # Pull the latest image from the registry to use as a cache
                cloudbuild_v1.BuildStep(
                    name="gcr.io/cloud-builders/docker",
                    entrypoint="bash",
                    args=[
                        "-c",
                        (
                            f"echo {creds.token} | docker login --username=oauth2accesstoken --password-stdin https://{source_env_region}-docker.pkg.dev "
                            f"&& docker pull {source_docker_image} "
                            f"&& docker tag {source_docker_image} {target_image}:{docker_image_tag} "
                        ),
                    ],
                ),
            ],
            # NOTE: This is what pushes the image to the registry
            images=[target_image, tagged_target_image],
        )
        # Submit the build to Cloud Build
        cloud_build_client = cloudbuild_v1.CloudBuildAsyncClient()
        operation = await cloud_build_client.create_build(
            project_id=target_gcp_project_id, build=build
        )
        build_url = f"https://console.cloud.google.com/cloud-build/builds/{operation.metadata.build.id}?project={target_gcp_project_id}"
        # Add logs to the table to the table
        workflow_progress.add_logs_row("build", build_url)
        await operation.result()

    # Return the docker image name
    return tagged_target_image


async def _import_failed_cloud_run_tf_state(
    tf_apply_command: TFApplyCommand, service_id: str
):
    tf_import_command = TFImportCommand(
        backend=tf_apply_command.backend,
        tf_module_dir=tf_apply_command.tf_module_dir,
        tf_state_prefix=tf_apply_command.tf_state_prefix,
        logs_file=tf_apply_command.logs_file,
        launchflow_state_url=tf_apply_command.launchflow_state_url,
        resource="google_cloud_run_v2_service.service",
        resource_id=service_id,
        tf_vars=tf_apply_command.tf_vars,
        drop_logs=True,
    )
    with tempfile.TemporaryDirectory() as tempdir:
        try:
            # NOTE: we drop logs because these logs are not useful
            # and they make it harder to see the above error.
            await tf_import_command.run(tempdir)
        except Exception:
            # Swallow exception for now
            logging.exception("Failed to import tf state on failure")
            return


async def _apply_cloud_run_tf(
    tf_backend_prefix: str,
    gcp_project_id: str,
    gcp_region: str,
    artifact_bucket: str,
    docker_image: str,
    project_name: str,
    environment_name: str,
    deployment_id: str,
    environment_service_account: str,
    logs_file: str,
    cloud_run_service: CloudRun,
    workflow_progress: WorkflowProgress,
    launchflow_state_url: str,
) -> Tuple[str, str]:
    with workflow_progress.step(
        "Setting up Cloud Run service", "Cloud Run service ready"
    ):
        # Cloud run doesn't support underscores in service names
        service_name = cloud_run_service.name.replace("_", "-")
        tf_vars = {
            "gcp_project_id": gcp_project_id,
            "gcp_region": gcp_region,
            "artifact_bucket": artifact_bucket,
            "docker_image": docker_image,
            "launchflow_project": project_name,
            "launchflow_environment": environment_name,
            "launchflow_deployment_id": deployment_id,
            "environment_service_account": environment_service_account,
            "service_name": service_name,
        }
        inputs = cloud_run_service.inputs()
        if inputs.cpu is not None:
            tf_vars["cpu"] = inputs.cpu
        if inputs.memory is not None:
            tf_vars["memory"] = inputs.memory
        if inputs.port is not None:
            tf_vars["port"] = inputs.port
        if inputs.publicly_accessible is not None:
            tf_vars["publicly_accessible"] = inputs.publicly_accessible
        if inputs.min_instance_count is not None:
            tf_vars["min_instance_count"] = inputs.min_instance_count
        if inputs.max_instance_count is not None:
            tf_vars["max_instance_count"] = inputs.max_instance_count
        if inputs.max_instance_request_concurrency is not None:
            tf_vars[
                "max_instance_request_concurrency"
            ] = inputs.max_instance_request_concurrency
        if inputs.invokers:
            tf_vars["invokers"] = inputs.invokers
        if inputs.custom_audiences:
            tf_vars["custom_audiences"] = inputs.custom_audiences
        if inputs.ingress:
            tf_vars["ingress"] = inputs.ingress

        service_tf_apply_command = TFApplyCommand(
            tf_module_dir="workflows/tf/services/gcp_cloud_run_service",
            backend=config.launchflow_yaml.backend,
            tf_state_prefix=tf_backend_prefix,
            tf_vars=tf_vars,
            logs_file=logs_file,
            launchflow_state_url=launchflow_state_url,
        )

        try:
            service_tf_outputs: Dict[str, Any] = await run_tofu(
                service_tf_apply_command
            )
        except exceptions.TofuApplyFailure as e:
            # NOTE: if the apply fails we attempt to import the state of the service
            # This is required because the service may have been created but the apply failed
            # and the state was not updated.
            await _import_failed_cloud_run_tf_state(
                service_tf_apply_command,
                service_id=f"projects/{gcp_project_id}/locations/{gcp_region}/services/{service_name}",
            )
            raise e

        service_url: Optional[str] = service_tf_outputs.get("service_url")
        gcp_id: Optional[str] = service_tf_outputs.get("gcp_id")
        if service_url is None:
            raise ValueError("Service URL not found in tf outputs")
        if gcp_id is None:
            raise ValueError("gcp id not found in tf outputs")

    return service_url, gcp_id


# Rule of Effective Java: public workflows should have 0 branching logic
# Make this specific to gcp cloud run (only fan out logic is on local build vs cloud build)
# deploy_gcp_cloud_run_build_local
# deploy_gcp_cloud_run_build_remote
# promote_gcp_cloud_run


# TODO: add tests that mock out the steps and verify the correct steps are called for each workflow type
async def deploy_gcp_cloud_run_build_remote(
    inputs: DeployCloudRunInputs,
    workflow_progress: WorkflowProgress,
) -> DeployGCPServiceOutputs:
    # Step 1 - Upload the source tarball to GCS
    await _upload_source_tarball_to_gcs(
        source_tarball_gcs_path=inputs.docker_build_inputs.source_tarball_path,
        artifact_bucket=inputs.gcp_environment_config.artifact_bucket,
        local_source_dir=inputs.docker_build_inputs.local_source_dir,
        workflow_progress=workflow_progress,
        build_ignore=inputs.gcp_service.build_ignore,
    )

    # Step 2 - Apply the tf that defines the docker repository
    docker_repository = await _apply_docker_repository_tf(
        inputs.launchflow_uri.tf_state_prefix(module="docker_artifact_registry"),
        inputs.gcp_environment_config.project_id,
        inputs.gcp_environment_config.default_region,
        inputs.launchflow_uri.service_name,
        inputs.infrastructure_logs,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="docker_artifact_registry"
        ),
    )

    # Step 3 - Build and push the docker image
    # TODO: either stream in the logs from cloud build, or just print the link to the cloud build url
    docker_image = await _run_docker_gcp_cloud_build(
        docker_repository=docker_repository,
        docker_image_name=inputs.launchflow_uri.service_name,
        docker_image_tag=inputs.deployment_id,
        gcs_source_bucket=inputs.docker_build_inputs.source_tarball_bucket,
        gcs_source_object=inputs.docker_build_inputs.source_tarball_path,
        gcp_project_id=inputs.gcp_environment_config.project_id,
        dockerfile_path=inputs.docker_build_inputs.dockerfile_path,
        artifact_bucket=inputs.gcp_environment_config.artifact_bucket,
        workflow_progress=workflow_progress,
    )

    # Step 4 - Apply the tf that defines the service
    service_url, gcp_id = await _apply_cloud_run_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="cloud_run_service"
        ),
        gcp_project_id=inputs.gcp_environment_config.project_id,
        gcp_region=inputs.gcp_environment_config.default_region,
        artifact_bucket=inputs.gcp_environment_config.artifact_bucket,
        docker_image=docker_image,
        project_name=inputs.launchflow_uri.project_name,
        environment_name=inputs.launchflow_uri.environment_name,
        environment_service_account=inputs.gcp_environment_config.service_account_email,
        deployment_id=inputs.deployment_id,
        logs_file=inputs.infrastructure_logs,
        cloud_run_service=inputs.gcp_service,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="cloud_run_service"
        ),
    )

    return DeployGCPServiceOutputs(
        docker_image=docker_image,
        service_url=service_url,
        gcp_id=gcp_id,
    )


async def deploy_gcp_cloud_run_build_local(
    inputs: DeployCloudRunInputs,
    workflow_progress: WorkflowProgress,
) -> DeployGCPServiceOutputs:
    # Step 1 - Apply the tf that defines the docker repository
    docker_repository = await _apply_docker_repository_tf(
        inputs.launchflow_uri.tf_state_prefix(module="docker_artifact_registry"),
        inputs.gcp_environment_config.project_id,
        inputs.gcp_environment_config.default_region,
        inputs.launchflow_uri.service_name,
        inputs.infrastructure_logs,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="docker_artifact_registry"
        ),
    )

    # Step 2 - Build and push the docker image
    docker_image = await _build_docker_image_local(
        docker_repository=docker_repository,
        docker_image_name=inputs.launchflow_uri.service_name,
        docker_image_tag=inputs.deployment_id,
        local_source_dir=inputs.docker_build_inputs.local_source_dir,
        dockerfile_path=inputs.docker_build_inputs.dockerfile_path,
        workflow_progress=workflow_progress,
        build_logs=inputs.build_logs,
    )

    # Step 3 - Apply the tf that defines the service
    service_url, gcp_id = await _apply_cloud_run_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="cloud_run_service"
        ),
        gcp_project_id=inputs.gcp_environment_config.project_id,
        gcp_region=inputs.gcp_environment_config.default_region,
        artifact_bucket=inputs.gcp_environment_config.artifact_bucket,
        docker_image=docker_image,
        project_name=inputs.launchflow_uri.project_name,
        environment_name=inputs.launchflow_uri.environment_name,
        environment_service_account=inputs.gcp_environment_config.service_account_email,
        deployment_id=inputs.deployment_id,
        logs_file=inputs.infrastructure_logs,
        cloud_run_service=inputs.gcp_service,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="cloud_run_service"
        ),
    )

    return DeployGCPServiceOutputs(
        docker_image=docker_image,
        service_url=service_url,
        gcp_id=gcp_id,
    )


async def promote_gcp_cloud_run(
    inputs: PromoteCloudRunInputs,
    workflow_progress: WorkflowProgress,
) -> DeployGCPServiceOutputs:
    # Step 1 - Apply the tf that defines the docker repository
    target_docker_repository = await _apply_docker_repository_tf(
        inputs.launchflow_uri.tf_state_prefix(module="docker_artifact_registry"),
        inputs.gcp_environment_config.project_id,
        inputs.gcp_environment_config.default_region,
        inputs.launchflow_uri.service_name,
        inputs.infrastructure_logs,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="docker_artifact_registry"
        ),
    )

    # Step 2 - Promote the existing docker image
    docker_image = await _promote_docker_image(
        source_env_region=inputs.gcp_promote_inputs.source_env_region,
        source_docker_image=inputs.gcp_promote_inputs.source_docker_image,
        target_docker_repository=target_docker_repository,
        docker_image_name=inputs.launchflow_uri.service_name,
        docker_image_tag=inputs.deployment_id,
        target_gcp_project_id=inputs.gcp_environment_config.project_id,
        target_artifact_bucket=inputs.gcp_environment_config.artifact_bucket,
        workflow_progress=workflow_progress,
    )

    # Step 3 - Apply the tf that defines the service
    service_url, gcp_id = await _apply_cloud_run_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="cloud_run_service"
        ),
        gcp_project_id=inputs.gcp_environment_config.project_id,
        gcp_region=inputs.gcp_environment_config.default_region,
        artifact_bucket=inputs.gcp_environment_config.artifact_bucket,
        docker_image=docker_image,
        project_name=inputs.launchflow_uri.project_name,
        environment_name=inputs.launchflow_uri.environment_name,
        environment_service_account=inputs.gcp_environment_config.service_account_email,
        deployment_id=inputs.deployment_id,
        logs_file=inputs.infrastructure_logs,
        cloud_run_service=inputs.gcp_service,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="cloud_run_service"
        ),
    )

    return DeployGCPServiceOutputs(
        docker_image=docker_image,
        service_url=service_url,
        gcp_id=gcp_id,
    )
