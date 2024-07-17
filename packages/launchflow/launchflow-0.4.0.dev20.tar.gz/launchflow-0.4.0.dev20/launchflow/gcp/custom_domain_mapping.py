import dataclasses

from launchflow.gcp.cloud_run_container import CloudRunServiceContainer
from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


@dataclasses.dataclass
class CustomDomainMappingOutputs(Outputs):
    ip_address: str
    registered_domain: str
    ssl_certificate_id: str


@dataclasses.dataclass
class CustomDomainMappingInputs(TofuInputs):
    domain: str
    cloud_run_service: str
    region: str


class CustomDomainMapping(GCPResource[CustomDomainMappingOutputs]):
    """A resource for mapping a custom domain to a Cloud Run service.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    ## Example Usage
    ```python
    import launchflow as lf

    custom_domain_mapping = lf.gcp.CustomDomainMapping("my-custom-domain-mapping", domain="my-domain.com", cloud_run=lf.gcp.CloudRunServiceContainer("my-cloud-run-service"))
    """

    product = ResourceProduct.GCP_CUSTOM_DOMAIN_MAPPING

    def __init__(
        self, name: str, *, domain: str, cloud_run: CloudRunServiceContainer
    ) -> None:
        """Create a new CustomDomainMapping resource.

        **Args**:
        - `name`: The name of the CustomDomainMapping resource. This must be globally unique.
        - `domain`: The domain to map to the Cloud Run service.
        - `cloud_run`: The Cloud Run service to map the domain to.
        """
        super().__init__(
            name=name,
            depends_on=[cloud_run],
        )
        self.domain = domain
        self.cloud_run = cloud_run

    def inputs(self, environment_type: EnvironmentType) -> CustomDomainMappingInputs:
        return CustomDomainMappingInputs(
            resource_id=self.resource_id,
            domain=self.domain,
            cloud_run_service=self.cloud_run.name,
            region=self.cloud_run.region,
        )
