import asyncio
import base64
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from docker.errors import BuildError

from launchflow import exceptions
from launchflow.aws.ecs_fargate import ECSFargate
from launchflow.config import config
from launchflow.flows.flow_logger import WorkflowProgress
from launchflow.workflows.commands.tf_commands import TFApplyCommand
from launchflow.workflows.deploy_aws_service.schemas import (
    DeployAWSServiceOutputs,
    DeployECSFargateInputs,
    PromoteECSFargateInputs,
)
from launchflow.workflows.utils import run_tofu, tar_source_in_memory


async def _upload_source_tarball_to_s3(
    source_tarball_s3_path: str,
    artifact_bucket: str,
    local_source_dir: str,
    workflow_progress: WorkflowProgress,
    build_ignore: List[str],
):
    try:
        import boto3
    except ImportError:
        raise exceptions.MissingAWSDependency()

    with workflow_progress.step(
        "Uploading source tarball to S3", "Source uploaded to S3"
    ):

        def upload_async():
            source_tarball = tar_source_in_memory(local_source_dir, build_ignore)

            try:
                bucket = boto3.resource(
                    "s3",
                    # TODO: Explore the idea of a launchflow.auth module that fetches
                    # default creds and passes them to boto3 (or throws a nice error)
                ).Bucket(artifact_bucket)
                bucket.upload_fileobj(source_tarball, source_tarball_s3_path)

            except Exception:
                raise exceptions.UploadSrcTarballFailed()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, upload_async)


async def _apply_docker_repository_tf(
    tf_backend_prefix: str,
    service_name: str,
    aws_account_id: str,
    aws_region: str,
    artifact_bucket: str,
    launchflow_project: str,
    launchflow_environment: str,
    vpc_id: str,
    source_tarball_path: str,
    launchflow_env_role_name: str,
    intrastructure_logs: str,
    workflow_progress: WorkflowProgress,
    launchflow_state_url: str,
) -> Tuple[str, str]:
    with workflow_progress.step(
        "Setting up Docker repository", "Docker repository ready"
    ):
        source_dir_path = "/".join(source_tarball_path.split("/")[:-1])
        docker_repo_tf_apply_command = TFApplyCommand(
            tf_module_dir="workflows/tf/docker/aws_codebuild_and_ecr",
            backend=config.launchflow_yaml.backend,
            tf_state_prefix=tf_backend_prefix,
            tf_vars={
                "aws_account_id": aws_account_id,
                "aws_region": aws_region,
                "service_name": service_name,
                "artifact_bucket": artifact_bucket,
                "launchflow_project": launchflow_project,
                "launchflow_environment": launchflow_environment,
                "vpc_id": vpc_id,
                "source_path": source_dir_path,
                "launchflow_env_role_name": launchflow_env_role_name,
            },
            logs_file=intrastructure_logs,
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
        codebuild_project_name: Optional[str] = docker_repo_tf_outputs.get(
            "codebuild_project_name"
        )
        if codebuild_project_name is None:
            raise ValueError("CodeBuild project name not found in tf outputs")

    return docker_repository, codebuild_project_name


def _get_build_status(client, build_id):
    response = client.batch_get_builds(ids=[build_id])
    if not response["builds"]:
        raise ValueError("No build found for the provided build ID.")
    build_status = response["builds"][0]["buildStatus"]
    return build_status


async def _poll_build_completion(client, build_id, poll_interval=10):
    """
    Polls the status of a build until it is completed or fails.

    :param client: Boto3 CodeBuild client
    :param build_id: ID of the build to poll
    :param poll_interval: Time in seconds between each poll
    """
    while True:
        build_status = _get_build_status(client, build_id)
        if build_status in ["SUCCEEDED"]:
            break
        elif build_status in ["FAILED", "FAULT", "TIMED_OUT", "STOPPED"]:
            raise ValueError(f"Build failed with status: {build_status}")
        else:
            await asyncio.sleep(poll_interval)  # Use asyncio.sleep for async waiting


async def _run_docker_aws_code_build(
    docker_repository: str,
    docker_image_tag: str,
    aws_account_id: str,
    aws_region: str,
    code_build_project_name: str,
    dockerfile_path: str,
    workflow_progress: WorkflowProgress,
):
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        raise exceptions.MissingAWSDependency()

    with workflow_progress.step("Building Docker image", "Docker image built"):
        client = boto3.client("codebuild", region_name=aws_region)

        try:
            response = client.start_build(
                projectName=code_build_project_name,
                environmentVariablesOverride=[
                    {
                        "name": "IMAGE_TAG",
                        "value": docker_image_tag,
                        "type": "PLAINTEXT",
                    },
                    {
                        "name": "DOCKERFILE_PATH",
                        "value": dockerfile_path,
                    },
                    {
                        "name": "BUILD_MODE",
                        "value": "build",
                        "type": "PLAINTEXT",
                    },
                ],
            )

            build_id = response["build"]["id"]

            build_url = f"https://{aws_region}.console.aws.amazon.com/codesuite/codebuild/{aws_account_id}/projects/{code_build_project_name}/build/{build_id}/?region={aws_region}"
            workflow_progress.add_logs_row("build", build_url)

            await _poll_build_completion(client, build_id)

        except ClientError as e:
            logging.exception("Error running AWS CodeBuild")
            raise e

    # Return the docker image name
    return f"{docker_repository}:{docker_image_tag}"


def _write_build_logs(file_path: str, log_stream, workflow_progress: WorkflowProgress):
    with open(file_path, "w") as f:
        for chunk in log_stream:
            if "stream" in chunk:
                f.write(chunk["stream"])
    # NOTE: we don't add the logs to the progress until after because the file doesn't exist yet
    workflow_progress.add_logs_row("build", file_path)


# TODO: Look into cleaning up old images. I noticed my docker images were taking up a lot of space
# after running this workflow multiple times
# TODO: consider moving this to a common docker module and pass in creds
async def _build_docker_image_local(
    aws_region: str,
    docker_repository: str,
    docker_image_name: str,
    docker_image_tag: str,
    local_source_dir: str,
    dockerfile_path: str,
    build_logs: str,
    workflow_progress: WorkflowProgress,
):
    try:
        from docker import errors, from_env
    except ImportError:
        raise exceptions.MissingDockerDependency()
    try:
        import boto3
    except ImportError:
        raise exceptions.MissingAWSDependency()

    with workflow_progress.step("Building Docker image", "Docker image built"):
        docker_client = from_env()
        latest_image_name = f"{docker_repository}/{docker_image_name}:latest"
        tagged_image_name = (
            f"{docker_repository}/{docker_image_name}:{docker_image_tag}"
        )
        # Authenticate with the docker registry
        ecr_client = boto3.client("ecr", region_name=aws_region)
        ecr_credentials = ecr_client.get_authorization_token()["authorizationData"][0]
        ecr_password = (
            base64.b64decode(ecr_credentials["authorizationToken"])
            .replace(b"AWS:", b"")
            .decode()
        )
        docker_client.login(
            username="AWS",
            password=ecr_password,
            registry=docker_repository.replace("https://", ""),
        )

        # Pull the latest image from the registry to use as a cache
        try:
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
    docker_repository: str,
    docker_image_tag: str,
    aws_account_id: str,
    aws_region: str,
    code_build_project_name: str,
    workflow_progress: WorkflowProgress,
):
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        raise exceptions.MissingAWSDependency()

    with workflow_progress.step("Promoting Docker image", "Docker image promoted"):
        # Fetch the source ecr registry credentials to pass into the build
        source_ecr_client = boto3.client("ecr", region_name=source_env_region)
        source_ecr_credentials = source_ecr_client.get_authorization_token()[
            "authorizationData"
        ][0]
        source_ecr_password = (
            base64.b64decode(source_ecr_credentials["authorizationToken"])
            .replace(b"AWS:", b"")
            .decode()
        )
        # Create the code build client
        code_build_client = boto3.client("codebuild", region_name=aws_region)

        split_image = source_docker_image.split(":")
        source_image_repo_name = split_image[0]
        source_image_tag = split_image[1]

        try:
            response = code_build_client.start_build(
                # NOTE: We override the source type since there's no source code to build for promotion
                sourceTypeOverride="NO_SOURCE",
                projectName=code_build_project_name,
                environmentVariablesOverride=[
                    {
                        "name": "IMAGE_TAG",
                        "value": docker_image_tag,
                        "type": "PLAINTEXT",
                    },
                    {
                        "name": "BUILD_MODE",
                        "value": "promotion",
                    },
                    {
                        "name": "SOURCE_ECR_PASSWORD",
                        "value": source_ecr_password,
                    },
                    {
                        "name": "SOURCE_ENV_IMAGE_REPO_NAME",
                        "value": source_image_repo_name,
                    },
                    {
                        "name": "SOURCE_ENV_IMAGE_TAG",
                        "value": source_image_tag,
                    },
                ],
            )

            build_id = response["build"]["id"]
            build_url = f"https://{aws_region}.console.aws.amazon.com/codesuite/codebuild/{aws_account_id}/projects/{code_build_project_name}/build/{build_id}/?region={aws_region}"
            workflow_progress.add_logs_row("build", build_url)

            await _poll_build_completion(code_build_client, build_id)

        except ClientError as e:
            logging.exception("Error running AWS CodeBuild")
            raise e

    # Return the docker image name
    return f"{docker_repository}:{docker_image_tag}"


async def _apply_ecs_fargate_tf(
    tf_backend_prefix: str,
    aws_account_id: str,
    aws_region: str,
    artifact_bucket: str,
    launchflow_project: str,
    launchflow_environment: str,
    deployment_id: str,
    vpc_id: str,
    docker_image: str,
    launchflow_env_role_name: str,
    infrastructure_logs: str,
    ecs_fargate_service: ECSFargate,
    workflow_progress: WorkflowProgress,
    launchflow_state_url: str,
) -> Tuple[str, str]:
    with workflow_progress.step(
        "Setting up ECS Fargate service", "ECS Fargate service ready"
    ):
        tf_vars = {
            "aws_account_id": aws_account_id,
            "aws_region": aws_region,
            "docker_image": docker_image,
            "artifact_bucket": artifact_bucket,
            "launchflow_project": launchflow_project,
            "launchflow_environment": launchflow_environment,
            "launchflow_deployment_id": deployment_id,
            "vpc_id": vpc_id,
            "launchflow_env_role_name": launchflow_env_role_name,
            "service_name": ecs_fargate_service.name,
        }
        # TODO: Expose optional tf vars for the user to set

        service_tf_apply_command = TFApplyCommand(
            tf_module_dir="workflows/tf/services/aws_ecs_fargate_service",
            backend=config.launchflow_yaml.backend,
            tf_state_prefix=tf_backend_prefix,
            tf_vars=tf_vars,
            logs_file=infrastructure_logs,
            launchflow_state_url=launchflow_state_url,
        )

        service_tf_outputs: Dict[str, Any] = await run_tofu(service_tf_apply_command)
        service_url: Optional[str] = service_tf_outputs.get("service_url")
        aws_arn: Optional[str] = service_tf_outputs.get("aws_arn")
        if service_url is None:
            raise ValueError("Service URL not found in tf outputs")
        if aws_arn is None:
            raise ValueError("AWS ARN not found in tf outputs")

    return service_url, aws_arn


# TODO: add tests that mock out the steps and verify the correct steps are called for each workflow type
async def deploy_aws_ecs_fargate_build_remote(
    inputs: DeployECSFargateInputs,
    workflow_progress: WorkflowProgress,
) -> DeployAWSServiceOutputs:
    launchflow_env_role_name = inputs.aws_environment_config.iam_role_arn.split("/")[-1]

    # Step 1 - Upload the source tarball to S3
    await _upload_source_tarball_to_s3(
        source_tarball_s3_path=inputs.docker_build_inputs.source_tarball_path,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        local_source_dir=inputs.docker_build_inputs.local_source_dir,
        workflow_progress=workflow_progress,
        build_ignore=inputs.aws_service.build_ignore,
    )

    # Step 2 - Apply the tf that defines the docker repository
    docker_repository, codebuild_project_name = await _apply_docker_repository_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="aws_codebuild_and_ecr"
        ),
        service_name=inputs.launchflow_uri.service_name,
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        launchflow_project=inputs.launchflow_uri.project_name,
        launchflow_environment=inputs.launchflow_uri.environment_name,
        vpc_id=inputs.aws_environment_config.vpc_id,
        source_tarball_path=inputs.docker_build_inputs.source_tarball_path,
        launchflow_env_role_name=launchflow_env_role_name,
        intrastructure_logs=inputs.infrastructure_logs,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="aws_codebuild_and_ecr"
        ),
    )

    # Step 3 - Build and push the docker image
    # TODO: either stream in the logs from code build, or just print the link to the code build url
    docker_image = await _run_docker_aws_code_build(
        docker_repository=docker_repository,
        docker_image_tag=inputs.deployment_id,
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        code_build_project_name=codebuild_project_name,
        dockerfile_path=inputs.docker_build_inputs.dockerfile_path,
        workflow_progress=workflow_progress,
    )

    # TODO: Create the ecs cluster in this flow, not at the env level
    # Step 4 - Apply the tf that defines the service
    service_url, aws_arn = await _apply_ecs_fargate_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="ecs_fargate_service"
        ),
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        launchflow_project=inputs.launchflow_uri.project_name,
        launchflow_environment=inputs.launchflow_uri.environment_name,
        deployment_id=inputs.deployment_id,
        vpc_id=inputs.aws_environment_config.vpc_id,
        docker_image=docker_image,
        launchflow_env_role_name=launchflow_env_role_name,
        infrastructure_logs=inputs.infrastructure_logs,
        ecs_fargate_service=inputs.aws_service,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="ecs_fargate_service"
        ),
    )

    return DeployAWSServiceOutputs(
        docker_image=docker_image,
        service_url=service_url,
        aws_arn=aws_arn,
    )


async def deploy_aws_ecs_fargate_build_local(
    inputs: DeployECSFargateInputs,
    workflow_progress: WorkflowProgress,
) -> DeployAWSServiceOutputs:
    launchflow_env_role_name = inputs.aws_environment_config.iam_role_arn.split("/")[-1]

    # Step 1 - Apply the tf that defines the docker repository
    docker_repository, _ = await _apply_docker_repository_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="aws_codebuild_and_ecr"
        ),
        service_name=inputs.launchflow_uri.service_name,
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        launchflow_project=inputs.launchflow_uri.project_name,
        launchflow_environment=inputs.launchflow_uri.environment_name,
        vpc_id=inputs.aws_environment_config.vpc_id,
        source_tarball_path=inputs.docker_build_inputs.source_tarball_path,
        launchflow_env_role_name=launchflow_env_role_name,
        intrastructure_logs=inputs.infrastructure_logs,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="aws_codebuild_and_ecr"
        ),
    )

    # Step 2 - Build and push the docker image
    docker_image = await _build_docker_image_local(
        aws_region=inputs.aws_environment_config.region,
        docker_repository=docker_repository,
        docker_image_name=inputs.launchflow_uri.service_name,
        docker_image_tag=inputs.deployment_id,
        local_source_dir=inputs.docker_build_inputs.local_source_dir,
        dockerfile_path=inputs.docker_build_inputs.dockerfile_path,
        workflow_progress=workflow_progress,
        build_logs=inputs.build_logs,
    )

    # Step 3 - Apply the tf that defines the service
    service_url, aws_arn = await _apply_ecs_fargate_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="ecs_fargate_service"
        ),
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        launchflow_project=inputs.launchflow_uri.project_name,
        launchflow_environment=inputs.launchflow_uri.environment_name,
        deployment_id=inputs.deployment_id,
        vpc_id=inputs.aws_environment_config.vpc_id,
        docker_image=docker_image,
        launchflow_env_role_name=launchflow_env_role_name,
        infrastructure_logs=inputs.infrastructure_logs,
        ecs_fargate_service=inputs.aws_service,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="ecs_fargate_service"
        ),
    )

    return DeployAWSServiceOutputs(
        docker_image=docker_image,
        service_url=service_url,
        aws_arn=aws_arn,
    )


async def promote_aws_ecs_fargate(
    inputs: PromoteECSFargateInputs,
    workflow_progress: WorkflowProgress,
) -> DeployAWSServiceOutputs:
    launchflow_env_role_name = inputs.aws_environment_config.iam_role_arn.split("/")[-1]

    # Step 1 - Apply the tf that defines the docker repository
    (
        target_docker_repository,
        codebuild_project_name,
    ) = await _apply_docker_repository_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="aws_codebuild_and_ecr"
        ),
        service_name=inputs.launchflow_uri.service_name,
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        launchflow_project=inputs.launchflow_uri.project_name,
        launchflow_environment=inputs.launchflow_uri.environment_name,
        vpc_id=inputs.aws_environment_config.vpc_id,
        source_tarball_path=inputs.aws_promote_inputs.source_tarball_path,
        launchflow_env_role_name=launchflow_env_role_name,
        intrastructure_logs=inputs.infrastructure_logs,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="aws_codebuild_and_ecr"
        ),
    )

    # Step 2 - Promote the existing docker image
    docker_image = await _promote_docker_image(
        source_env_region=inputs.aws_promote_inputs.source_env_region,
        source_docker_image=inputs.aws_promote_inputs.source_docker_image,
        docker_repository=target_docker_repository,
        docker_image_tag=inputs.deployment_id,
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        code_build_project_name=codebuild_project_name,
        workflow_progress=workflow_progress,
    )

    # Step 3 - Apply the tf that defines the service
    service_url, aws_arn = await _apply_ecs_fargate_tf(
        tf_backend_prefix=inputs.launchflow_uri.tf_state_prefix(
            module="ecs_fargate_service"
        ),
        aws_account_id=inputs.aws_environment_config.account_id,
        aws_region=inputs.aws_environment_config.region,
        artifact_bucket=inputs.aws_environment_config.artifact_bucket,
        launchflow_project=inputs.launchflow_uri.project_name,
        launchflow_environment=inputs.launchflow_uri.environment_name,
        deployment_id=inputs.deployment_id,
        vpc_id=inputs.aws_environment_config.vpc_id,
        docker_image=docker_image,
        launchflow_env_role_name=launchflow_env_role_name,
        infrastructure_logs=inputs.infrastructure_logs,
        ecs_fargate_service=inputs.aws_service,
        workflow_progress=workflow_progress,
        launchflow_state_url=inputs.launchflow_uri.launchflow_tofu_state_url(
            lock_id=inputs.lock_id, module="ecs_fargate_service"
        ),
    )

    return DeployAWSServiceOutputs(
        docker_image=docker_image,
        service_url=service_url,
        aws_arn=aws_arn,
    )
