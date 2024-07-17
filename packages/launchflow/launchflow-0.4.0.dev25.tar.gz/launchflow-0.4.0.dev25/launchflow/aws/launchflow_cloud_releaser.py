import dataclasses

import httpx
import rich

import launchflow
from launchflow import exceptions
from launchflow.backend import LaunchFlowBackend
from launchflow.clients.accounts_client import AccountsSyncClient
from launchflow.clients.environments_client import EnvironmentsSyncClient
from launchflow.config import config
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs

try:
    import boto3
except ImportError:
    boto3 = None


from launchflow.aws.resource import AWSResource


@dataclasses.dataclass
class LaunchFlowCloudReleaserOutputs(Outputs):
    code_build_project_arn: str
    releaser_role_arn: str


@dataclasses.dataclass
class LaunchFlowCloudReleaserInputs(TofuInputs):
    launchflow_cloud_aws_account_id: str
    launchflow_cloud_role_name: str
    launchflow_cloud_external_role_id: str


class LaunchFlowCloudReleaser(AWSResource[LaunchFlowCloudReleaserOutputs]):
    """A resource for connecting a LaunchFlow environment to LaunchFlow Cloud.

    This will create an AWS IAM role and policy that can push new builds to your services.
    Build will be pushed using a Code Build project. For more information see our [GitHub integration docs](https://docs.launchflow.com/docs/launchflow-cloud/github-deployments).

    Connecting your environment with `lf cloud connect ${ENV_NAME}` will automatically create this resource.

    ## Utility Methods
    """

    product = ResourceProduct.AWS_LAUNCHFLOW_CLOUD_RELEASER

    def __init__(self, name: str = "launchflow-releaser") -> None:
        """Create a new LaunchFlowCloudReleaser resource."""
        super().__init__(
            name=name,
            resource_id=f"{name}-{launchflow.project}-{launchflow.environment}",
        )

    def inputs(
        self, environment_type: EnvironmentType
    ) -> LaunchFlowCloudReleaserInputs:
        """Get the inputs for the LaunchFlowCloudReleaser resource.

        **Args:**
        - `environment_type` (EnvironmentType): The type of environment.

        **Returns:**
        - LaunchFlowCloudReleaserInputs: The inputs for the LaunchFlowCloudReleaser resource.
        """
        backend = config.launchflow_yaml.backend
        if not isinstance(backend, LaunchFlowBackend):
            raise exceptions.LaunchFlowBackendRequired()
        with httpx.Client() as http_client:
            client = AccountsSyncClient(
                http_client=http_client,
                service_address=backend.lf_cloud_url,
            )
            connect = client.connect(config.get_account_id())
        return LaunchFlowCloudReleaserInputs(
            resource_id=self.resource_id,
            launchflow_cloud_role_name=connect.aws_role_name,
            launchflow_cloud_aws_account_id=connect.aws_account_id,
            launchflow_cloud_external_role_id=connect.aws_external_role_id,
        )

    async def connect_to_launchflow(self):
        """Connect the environment to LaunchFlow Cloud."""
        outputs = await self.outputs_async()
        backend = config.launchflow_yaml.backend
        if not isinstance(backend, LaunchFlowBackend):
            raise exceptions.LaunchFlowBackendRequired()
        with httpx.Client() as http_client:
            client = EnvironmentsSyncClient(
                http_client=http_client,
                launch_service_url=backend.lf_cloud_url,
                launchflow_account_id=config.get_account_id(),
            )
            client.connect_aws(
                project_name=launchflow.project,
                env_name=launchflow.environment,
                code_build_project_arn=outputs.code_build_project_arn,
                releaser_role_arn=outputs.releaser_role_arn,
                resource_name=self.name,
            )
        rich.print(
            f"[green]Environment `{launchflow.environment}` is now connected to LaunchFlow Cloud![/green]\n"
        )
        rich.print(
            f"Releases will be pushed using the IAM role we created for you: `{outputs.releaser_role_arn}` and they will be run in Code Build Project: `{outputs.code_build_project_arn}`. You can learn more at: https://docs.launchflow.com/docs/launchflow-cloud/github-deployments\n"
        )
        rich.print(
            "We have granted the releaser IAM role the minimum required permissions to deploy your app to ECS Fargate. "
            "You may grant any additional permissions as needed via the cloud console."
        )
