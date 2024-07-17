from dataclasses import dataclass
from typing import List, Literal, Optional

from launchflow import exceptions
from launchflow.gcp.artifact_registry_repository import (
    ArtifactRegistryRepository,
    RegistryFormat,
)
from launchflow.gcp.cloud_run_container import CloudRunServiceContainer
from launchflow.gcp.custom_domain_mapping import CustomDomainMapping
from launchflow.gcp.service import GCPService
from launchflow.models.enums import ServiceProduct
from launchflow.node import Inputs
from launchflow.resource import Resource
from launchflow.service import DNSOutputs, ServiceOutputs


@dataclass
class CloudRunInputs(Inputs):
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


class CloudRun(GCPService):
    """A service hosted on GCP Cloud Run.

    ****Example usage:****
    ```python
    import launchflow as lf

    service = lf.gcp.CloudRun("my-service", cpu=4)
    ```

    **NOTE:** This will create the following infrastructure in your GCP project:
    - A [Cloud Run](https://cloud.google.com/run) service with the specified configuration.
    - A [Load Balancer](https://cloud.google.com/load-balancing) to route traffic to the service.
    - A [Cloud Build](https://cloud.google.com/build) trigger that builds and deploys the service.
    - An [Artifact Registry](https://cloud.google.com/artifact-registry) repository to store the service's Docker image.
    """

    product = ServiceProduct.GCP_CLOUD_RUN

    def __init__(
        self,
        name: str,
        # build inputs
        dockerfile: str = "Dockerfile",
        build_directory: str = ".",
        build_ignore: List[str] = [],
        # cloud run inputs
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
        # custom domain inputs
        domain: Optional[str] = None,
    ) -> None:
        """Creates a new Cloud Run service.

        **Args:**
        - `name`: The name of the service.
        - `build_directory`: The directory to build the service from. This should be a relative path from the project root where your `launchflow.yaml` is defined.
        - `dockerfile`: The Dockerfile to use for building the service. This should be a relative path from the `build_directory`.
        - `build_ignore`: A list of files to ignore when building the service. This can be in the same syntax you would use for a `.gitignore`.
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
        - `domain`: The custom domain to map to the service.
        """
        super().__init__(
            name=name,
            dockerfile=dockerfile,
            build_directory=build_directory,
            build_ignore=build_ignore,
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

        # Resources - flows should not access these directly
        self._artifact_registry = ArtifactRegistryRepository(
            f"{name}-repository", format=RegistryFormat.DOCKER
        )
        self._artifact_registry.resource_id = name
        self._cloud_run_service_container = CloudRunServiceContainer(
            f"{name}-container",
            region=region,
            cpu=cpu,
            memory=memory,
            port=port,
            publicly_accessible=publicly_accessible,
            min_instance_count=min_instance_count,
            max_instance_count=max_instance_count,
            max_instance_request_concurrency=max_instance_request_concurrency,
            invokers=invokers,
            custom_audiences=custom_audiences,
            ingress=ingress,
        )
        self._cloud_run_service_container.resource_id = name

        if domain:
            self._custom_domain_mapping = CustomDomainMapping(
                f"{name}-domain-mapping",
                domain=domain,
                cloud_run=self._cloud_run_service_container,
            )
            self._custom_domain_mapping.resource_id = name
        else:
            self._custom_domain_mapping = None

    def inputs(self) -> CloudRunInputs:
        return CloudRunInputs(
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
        )

    def resources(self) -> List[Resource]:
        to_return = [
            self._artifact_registry,
            self._cloud_run_service_container,
        ]
        if self._custom_domain_mapping:
            to_return.append(self._custom_domain_mapping)
        return to_return

    def outputs(self) -> ServiceOutputs:
        try:
            service_container_outputs = self._cloud_run_service_container.outputs()
            artifact_registry_outputs = self._artifact_registry.outputs()
        except exceptions.ResourceOutputsNotFound:
            raise exceptions.ServiceOutputsNotFound(service_name=self.name)

        dns_outputs = None
        if self._custom_domain_mapping is not None:
            try:
                custom_domain_outputs = self._custom_domain_mapping.outputs()
            except exceptions.ResourceOutputsNotFound:
                raise exceptions.ServiceOutputsNotFound(service_name=self.name)
            dns_outputs = DNSOutputs(
                domain=custom_domain_outputs.registered_domain,
                ip_address=custom_domain_outputs.ip_address,
            )

        if artifact_registry_outputs.docker_repository is None:
            raise ValueError("Docker repository not found in artifact registry outputs")

        service_outputs = ServiceOutputs(
            service_url=service_container_outputs.service_url,
            docker_repository=artifact_registry_outputs.docker_repository,
            dns_outputs=dns_outputs,
        )
        service_outputs.gcp_id = service_container_outputs.gcp_id

        return service_outputs
