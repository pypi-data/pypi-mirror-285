from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

import launchflow as lf
from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.models.flow_state import EnvironmentState
from launchflow.node import Outputs
from launchflow.resource import TofuInputs


@dataclass
class CloudRunServiceContainerInputs(TofuInputs):
    region: Optional[str]
    cpu: Optional[int]
    memory: Optional[str]
    port: Optional[int]
    publicly_accessible: Optional[bool]
    min_instance_count: Optional[int]
    max_instance_count: Optional[int]
    max_instance_request_concurrency: Optional[int]
    invokers: Optional[List[str]]
    custom_audiences: Optional[List[str]]
    ingress: Optional[
        Literal[
            "INGRESS_TRAFFIC_ALL",
            "INGRESS_TRAFFIC_INTERNAL_ONLY",
            "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
        ]
    ]
    launchflow_environment: str
    launchflow_project: str


@dataclass
class CloudRunServiceContainerOutputs(Outputs):
    service_url: str


class CloudRunServiceContainer(GCPResource[CloudRunServiceContainerOutputs]):
    """A container for a service running on Cloud Run.

    ****Example usage:****
    ```python
    import launchflow as lf

    service_container = lf.gcp.CloudRunServiceContainer("my-service-container", cpu=4)
    ```
    """

    product = ResourceProduct.GCP_CLOUD_RUN_SERVICE_CONTAINER

    def __init__(
        self,
        name: str,
        region: Optional[str] = None,
        cpu: Optional[int] = None,
        memory: Optional[str] = None,
        port: Optional[int] = None,
        publicly_accessible: Optional[bool] = None,
        min_instance_count: Optional[int] = None,
        max_instance_count: Optional[int] = None,
        max_instance_request_concurrency: Optional[int] = None,
        invokers: Optional[List[str]] = None,
        custom_audiences: Optional[List[str]] = None,
        ingress: Optional[
            Literal[
                "INGRESS_TRAFFIC_ALL",
                "INGRESS_TRAFFIC_INTERNAL_ONLY",
                "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
            ]
        ] = None,
    ) -> None:
        """Creates a new Cloud Run Service container.

        **Args:**
        - `name`: The name of the service.
        - `region`: The region to deploy the service to.
        - `cpu`: The number of CPUs to allocate to each instance of the service.
        - `memory`: The amount of memory to allocate to each instance of the service.
        - `port`: The port the service listens on.
        - `publicly_accessible`: Whether the service is publicly accessible. Defaults to True.
        - `min_instance_count`: The minimum number of instances to keep running.
        - `max_instance_count`: The maximum number of instances to run.
        - `max_instance_request_concurrency`: The maximum number of requests each instance can handle concurrently.
        - `invokers`: A list of invokers that can access the service.
        - `custom_audiences`: A list of custom audiences that can access the service. See: [https://cloud.google.com/run/docs/configuring/custom-audiences](https://cloud.google.com/run/docs/configuring/custom-audiences)
        - `ingress`: The ingress settings for the service. See: [https://cloud.google.com/run/docs/securing/ingress](https://cloud.google.com/run/docs/configuring/custom-audiences)
        """
        super().__init__(
            name=name,
            replacement_arguments={"region"},
        )
        self.region = region
        self.cpu = cpu
        self.memory = memory
        self.port = port
        self.publicly_accessible = publicly_accessible
        self.min_instance_count = min_instance_count
        self.max_instance_count = max_instance_count
        self.max_instance_request_concurrency = max_instance_request_concurrency
        self.invokers = invokers
        self.custom_audiences = custom_audiences
        self.ingress = ingress

    def import_resource(self, environment: EnvironmentState) -> Dict[str, str]:
        location = self.region or environment.gcp_config.default_region
        return {
            "google_cloud_run_v2_service.service": f"projects/{environment.gcp_config.project_id}/locations/{location}/services/{self.resource_id}",
        }

    def inputs(
        self, environment_type: EnvironmentType
    ) -> CloudRunServiceContainerInputs:
        return CloudRunServiceContainerInputs(
            resource_id=self.resource_id,
            region=self.region,
            cpu=self.cpu,
            memory=self.memory,
            port=self.port,
            publicly_accessible=self.publicly_accessible,
            min_instance_count=self.min_instance_count,
            max_instance_count=self.max_instance_count,
            max_instance_request_concurrency=self.max_instance_request_concurrency,
            invokers=self.invokers,
            custom_audiences=self.custom_audiences,
            ingress=self.ingress,
            launchflow_environment=lf.environment,
            launchflow_project=lf.project,
        )
