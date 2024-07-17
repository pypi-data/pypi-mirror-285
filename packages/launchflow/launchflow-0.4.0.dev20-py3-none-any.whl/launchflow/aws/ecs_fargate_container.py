from dataclasses import dataclass
from typing import Union

from launchflow.aws.ecs_cluster import ECSCluster
from launchflow.aws.resource import AWSResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


# TODO: Add ECS Fargate specific options
@dataclass
class ECSFargateServiceContainerInputs(TofuInputs):
    resource_name: str
    ecs_cluster_name: str


@dataclass
class ECSFargateServiceContainerOutputs(Outputs):
    public_ip: str


class ECSFargateServiceContainer(AWSResource[ECSFargateServiceContainerOutputs]):
    """A container for a service running on ECS Fargate.

    ****Example usage:****
    ```python
    import launchflow as lf

    service_container = lf.aws.ECSFargateServiceContainer("my-service-container")
    ```
    TODO: flush out these docs more
    """

    product = ResourceProduct.AWS_ECS_FARGATE_SERVICE_CONTAINER

    def __init__(self, name: str, ecs_cluster: Union[ECSCluster, str]) -> None:
        """Creates a new ECS Fargate service container.

        **Args:**
         - TODO
        """
        depends_on = []
        if isinstance(ecs_cluster, ECSCluster):
            self._ecs_cluster_name = ecs_cluster.resource_id
            depends_on.append(ecs_cluster)
        elif isinstance(ecs_cluster, str):
            self._ecs_cluster_name = ecs_cluster
        else:
            raise ValueError("cluster must be an ECSCluster or a str")
        super().__init__(name=name, depends_on=depends_on)

    def inputs(
        self, environment_type: EnvironmentType
    ) -> ECSFargateServiceContainerInputs:
        return ECSFargateServiceContainerInputs(
            resource_id=self.resource_id,
            resource_name=self.name,
            ecs_cluster_name=self._ecs_cluster_name,
        )
