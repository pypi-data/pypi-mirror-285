import dataclasses

from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


@dataclasses.dataclass
class WorkbenchInstanceOutputs(Outputs):
    instance_id: str
    instance_url: str


@dataclasses.dataclass
class WorkbenchInstanceInputs(TofuInputs):
    pass


class WorkbenchInstance(GCPResource[WorkbenchInstanceOutputs]):
    product = ResourceProduct.GCP_WORKBENCH_INSTANCE

    def __init__(
        self,
        name: str,
        # TODO: Add the rest of the inputs
    ) -> None:
        super().__init__(name=name)


    def inputs(self, environment_type: EnvironmentType) -> WorkbenchInstanceInputs:
        return WorkbenchInstanceInputs(
            resource_id=self.resource_id,
        )
