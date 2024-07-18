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
    cpu: int = 256
    memory: int = 512
    port: int = 80
    desired_count: int = 1


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
    """

    product = ResourceProduct.AWS_ECS_FARGATE_SERVICE_CONTAINER

    def __init__(
        self,
        name: str,
        ecs_cluster: Union[ECSCluster, str],
        cpu: int = 256,
        memory: int = 512,
        port: int = 80,
        desired_count: int = 1,
    ) -> None:
        """Creates a new ECS Fargate service container.

        **Args:**
        - `name (str)`: The name of the ECS Fargate service container.
        - `ecs_cluster (Union[ECSCluster, str])`: The ECS cluster or the name of the ECS cluster.
        - `cpu (int)`: The CPU units to allocate to the container. Defaults to 256.
        - `memory (int)`: The memory to allocate to the container. Defaults to 512.
        - `port (int)`: The port the container listens on. Defaults to 80.
        - `desired_count (int)`: The number of tasks to run. Defaults to 1.

        **Raises:**
         - `ValueError`: If `ecs_cluster` is not an instance of `ECSCluster` or `str`.
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
        self.cpu = cpu
        self.memory = memory
        self.port = port
        self.desired_count = desired_count

    def inputs(
        self, environment_type: EnvironmentType
    ) -> ECSFargateServiceContainerInputs:
        """Get the inputs for the ECS Fargate service container resource.

        **Args:**
         - `environment_type (EnvironmentType)`: The environment type.

        **Returns:**
         - `ECSFargateServiceContainerInputs`: The inputs required for the ECS Fargate service container.
        """
        return ECSFargateServiceContainerInputs(
            resource_id=self.resource_id,
            resource_name=self.name,
            ecs_cluster_name=self._ecs_cluster_name,
            cpu=self.cpu,
            memory=self.memory,
            port=self.port,
            desired_count=self.desired_count,
        )
