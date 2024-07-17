from dataclasses import dataclass
from typing import List

import pkg_resources

import launchflow as lf
from launchflow import exceptions
from launchflow.aws.codebuild_project import (
    Cache,
    CloudWatchLogsConfig,
    CodeBuildProject,
    Environment,
    EnvironmentVariable,
    LogsConfig,
    Source,
)
from launchflow.aws.ecr_repository import ECRRepository
from launchflow.aws.ecs_cluster import ECSCluster
from launchflow.aws.ecs_fargate_container import ECSFargateServiceContainer
from launchflow.aws.service import AWSService, AWSServiceOutputs
from launchflow.models.enums import ServiceProduct
from launchflow.node import Inputs
from launchflow.resource import Resource


# TODO: Add ECS Fargate specific options
@dataclass
class ECSFargateInputs(Inputs):
    pass


class ECSFargate(AWSService):
    """A service hosted on AWS ECS Fargate.

    Like all [Services](/docs/concepts/services), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html).


    ## Example Usage
    ```python
    import launchflow as lf

    # Automatically creates / connects to an ECS Fargate Service in your AWS account
    service = lf.aws.ECSFargate("my-service")
    ```

    **NOTE:** This will create the following infrastructure in your AWS account:
    - A [ECS Fargate](https://aws.amazon.com/fargate/) service with the specified configuration.
    - An [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing) to route traffic to the service.
    - A [Code Build](https://aws.amazon.com/codebuild) project that builds and deploys Docker images for the service.
    - An [Elastic Container Registry](https://aws.amazon.com/ecr) repository to store the service's Docker image.
    """

    product = ServiceProduct.AWS_ECS_FARGATE

    def __init__(
        self,
        name: str,
        dockerfile: str = "Dockerfile",
        build_directory: str = ".",
        build_ignore: List[str] = [],
    ) -> None:
        """Creates a new ECS Fargate service.

        **Args:**
        - `name`: The name of the service.
        - `build_directory`: The directory to build the service from. This should be a relative path from the project root where your `launchflow.yaml` is defined.
        - `dockerfile`: The Dockerfile to use for building the service. This should be a relative path from the `build_directory`.
        - `build_ignore`: A list of files to ignore when building the service. This can be in the same syntax you would use for a `.gitignore`.
        """
        super().__init__(
            name=name,
            dockerfile=dockerfile,
            build_directory=build_directory,
            build_ignore=build_ignore,
        )
        resource_id_with_launchflow_prefix = f"{lf.project}-{lf.environment}-{name}"
        # Resources - flows should not access these directly
        self._ecr = ECRRepository(
            f"{name}-ecr", force_delete=True, image_tag_mutability="MUTABLE"
        )
        self._ecr.resource_id = resource_id_with_launchflow_prefix

        # Builds an absolute path to the buildspec.yml file packaged with launchflow
        buildspec_path = pkg_resources.resource_filename(
            "launchflow", "workflows/tf/resources/aws_codebuild_project/buildspec.yml"
        )
        self._code_build_project = CodeBuildProject(
            f"{name}-codebuild",
            environment=Environment(
                compute_type="BUILD_GENERAL1_SMALL",
                image="aws/codebuild/standard:5.0",
                type="LINUX_CONTAINER",
                image_pull_credentials_type="CODEBUILD",
                environment_variables=[
                    EnvironmentVariable("IMAGE_REPO_NAME", self._ecr.resource_id),
                    EnvironmentVariable("IMAGE_TAG", "latest"),
                    EnvironmentVariable("SOURCE_TAR_NAME", "source.tar.gz"),
                ],
            ),
            build_source=Source(type="NO_SOURCE", buildspec_path=buildspec_path),
            cache=Cache(
                # TODO: Add cache options
                type="NO_CACHE"
            ),
            logs_config=LogsConfig(
                cloud_watch_logs=CloudWatchLogsConfig(
                    status="ENABLED",
                )
            ),
        )
        self._code_build_project.resource_id = resource_id_with_launchflow_prefix
        self._code_build_project.depends_on.append(self._ecr)

        self._ecs_cluster = ECSCluster(f"{name}-cluster")
        self._ecs_cluster.resource_id = resource_id_with_launchflow_prefix
        self._ecs_fargate_service_container = ECSFargateServiceContainer(
            name, self._ecs_cluster
        )
        self._ecs_fargate_service_container.resource_id = (
            resource_id_with_launchflow_prefix
        )

        # TODO: Add a load balancer resource type

    def inputs(self) -> ECSFargateInputs:
        return ECSFargateInputs()

    def resources(self) -> List[Resource]:
        return [
            self._ecr,
            self._code_build_project,
            self._ecs_cluster,
            self._ecs_fargate_service_container,
        ]

    def outputs(self) -> AWSServiceOutputs:
        try:
            ecr_outputs = self._ecr.outputs()
            code_build_outputs = self._code_build_project.outputs()
            fargate_outputs = self._ecs_fargate_service_container.outputs()
        except exceptions.ResourceOutputsNotFound:
            raise exceptions.ServiceOutputsNotFound(service_name=self.name)

        service_outputs = AWSServiceOutputs(
            service_url=f"http://{fargate_outputs.public_ip}",
            docker_repository=ecr_outputs.repository_url,
            code_build_project_name=code_build_outputs.project_name,
            # TODO: Support custom domains for ECS Fargate
            dns_outputs=None,
        )
        service_outputs.aws_arn = fargate_outputs.aws_arn

        return service_outputs
