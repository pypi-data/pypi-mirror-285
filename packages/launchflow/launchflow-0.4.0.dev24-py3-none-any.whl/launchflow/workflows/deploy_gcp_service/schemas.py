from dataclasses import dataclass
from typing import Optional

from launchflow.gcp.cloud_run import CloudRun
from launchflow.models.flow_state import GCPEnvironmentConfig
from launchflow.models.launchflow_uri import LaunchFlowURI
from launchflow.workflows.common_inputs import DockerBuildInputs


@dataclass
class DeployCloudRunInputs:
    gcp_service: CloudRun
    deployment_id: str
    lock_id: str
    launchflow_uri: LaunchFlowURI
    gcp_environment_config: GCPEnvironmentConfig
    docker_build_inputs: DockerBuildInputs
    infrastructure_logs: str
    build_logs: str


@dataclass
class DeployGCPServiceOutputs:
    docker_image: Optional[str]
    service_url: Optional[str]
    gcp_id: Optional[str]


@dataclass
class GCPPromotionInputs:
    source_docker_image: str
    source_env_region: str


@dataclass
class PromoteCloudRunInputs:
    gcp_service: CloudRun
    deployment_id: str
    lock_id: str
    launchflow_uri: LaunchFlowURI
    gcp_environment_config: GCPEnvironmentConfig
    gcp_promote_inputs: GCPPromotionInputs
    infrastructure_logs: str
