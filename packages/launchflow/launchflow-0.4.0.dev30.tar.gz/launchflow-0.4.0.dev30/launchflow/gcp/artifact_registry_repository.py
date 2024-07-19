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

        **Args:**
        - `name (str)`: The name of the ArtifactRegistryRepository resource. This must be globally unique.
        - `format (Union[str, RegistryFormat])`: The format of the ArtifactRegistryRepository.
        - `location (Optional[str])`: The location of the ArtifactRegistryRepository. Defaults to the default region of the GCP project.
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
        """Import the Artifact Registry repository resource.

        **Args:**
        - `environment (EnvironmentState)`: The environment state.

        **Returns:**
        - A dictionary with the resource information.
        """
        location = self.location or environment.gcp_config.default_region
        return {
            "google_artifact_registry_repository.repository": f"projects/{environment.gcp_config.project_id}/locations/{location}/repositories/{self.resource_id}",
        }

    def inputs(self, environment_type: EnvironmentType) -> ArtifactRegistryInputs:
        """Get the inputs for the Artifact Registry repository resource.

        **Args:**
        - `environment_type (EnvironmentType)`: The type of environment.

        **Returns:**
        - ArtifactRegistryInputs: The inputs for the Artifact Registry repository resource.
        """
        return ArtifactRegistryInputs(
            resource_id=self.resource_id,
            format=self.format.value,
            location=self.location,
        )
