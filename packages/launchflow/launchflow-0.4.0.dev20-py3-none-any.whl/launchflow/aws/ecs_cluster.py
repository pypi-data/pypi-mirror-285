from dataclasses import dataclass

from launchflow.aws.resource import AWSResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


@dataclass
class ECSClusterInputs(TofuInputs):
    pass


@dataclass
class ECSClusterOutputs(Outputs):
    cluster_name: str


class ECSCluster(AWSResource[ECSClusterOutputs]):
    """An ECS cluster.

    ****Example usage:****
    ```python
    import launchflow as lf

    ecs_cluster = lf.aws.ECSCluster("my-cluster")
    ```
    TODO: flush out these docs more
    """

    product = ResourceProduct.AWS_ECS_CLUSTER

    def __init__(self, name: str) -> None:
        """Creates a new ECS cluster.

        **Args:**
         - TODO
        """
        super().__init__(name=name)

    def inputs(self, environment_type: EnvironmentType) -> ECSClusterInputs:
        return ECSClusterInputs(resource_id=self.resource_id)
