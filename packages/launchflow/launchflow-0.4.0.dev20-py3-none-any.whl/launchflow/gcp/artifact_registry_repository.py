from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union

from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.models.flow_state import EnvironmentState
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


@dataclass
class ArtifactRegistryOutputs(Outputs):
    # NOTE: This is only set if the format is DOCKER
    docker_repository: Optional[str] = None


@dataclass
class ArtifactRegistryInputs(TofuInputs):
    format: str
    location: Optional[str] = None


class RegistryFormat(Enum):
    DOCKER = "DOCKER"
    MAVEN = "MAVEN"
    NPM = "NPM"
    PYTHON = "PYTHON"
    APT = "APT"
    YUM = "YUM"
    KUBEFLOW = "KUBEFLOW"
    GENERIC = "GENERIC"


class ArtifactRegistryRepository(GCPResource[ArtifactRegistryOutputs]):
    """A resource for creating an artifact registry repository.
    Can be used to store docker images, python packages, and more.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    ## Example Usage
    ```python
    import launchflow as lf

    artifact_registry = lf.gcp.ArtifactRegistryRepository("my-artifact-registry", format="DOCKER")
    ```
    """
    product = ResourceProduct.GCP_ARTIFACT_REGISTRY_REPOSITORY

    def __init__(
        self,
        name: str,
        format: Union[str, RegistryFormat],
        location: Optional[str] = None,
    ) -> None:
        """Create a new ArtifactRegistryRepository resource.

        **Args**:
        - `name`: The name of the ArtifactRegistryRepository resource. This must be globally unique.
        - `format`: The format of the ArtifactRegistryRepository.
        - `location`: The location of the ArtifactRegistryRepository. Defaults to the default region of the GCP project.
        """
        super().__init__(
            name=name,
            replacement_arguments={"format", "location"},
        )
        if isinstance(format, str):
            format = RegistryFormat(format.upper())
        self.format = format
        self.location = location

    def import_resource(self, environment: EnvironmentState) -> Dict[str, str]:
        location = self.location or environment.gcp_config.default_region
        return {
            "google_artifact_registry_repository.repository": f"projects/{environment.gcp_config.project_id}/locations/{location}/repositories/{self.resource_id}",
        }

    def inputs(self, environment_type: EnvironmentType) -> ArtifactRegistryInputs:
        return ArtifactRegistryInputs(
            resource_id=self.resource_id,
            format=self.format.value,
            location=self.location,
        )
