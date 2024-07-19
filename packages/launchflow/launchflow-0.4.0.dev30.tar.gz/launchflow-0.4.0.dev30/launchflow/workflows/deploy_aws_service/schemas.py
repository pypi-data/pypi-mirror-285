from dataclasses import dataclass
from typing import Optional

from launchflow.aws.ecs_fargate import ECSFargate
from launchflow.models.flow_state import AWSEnvironmentConfig
from launchflow.models.launchflow_uri import LaunchFlowURI
from launchflow.workflows.common_inputs import DockerBuildInputs


@dataclass
class DeployECSFargateInputs:
    aws_service: ECSFargate
    deployment_id: str
    lock_id: str
    launchflow_uri: LaunchFlowURI
    aws_environment_config: AWSEnvironmentConfig
    docker_build_inputs: DockerBuildInputs
    infrastructure_logs: str
    build_logs: str


@dataclass
class DeployAWSServiceOutputs:
    docker_image: Optional[str]
    service_url: Optional[str]
    aws_arn: Optional[str]


@dataclass
class AWSPromotionInputs:
    source_docker_image: str
    source_env_region: str
    source_tarball_path: str


@dataclass
class PromoteECSFargateInputs:
    aws_service: ECSFargate
    deployment_id: str
    lock_id: str
    launchflow_uri: LaunchFlowURI
    aws_environment_config: AWSEnvironmentConfig
    aws_promote_inputs: AWSPromotionInputs
    infrastructure_logs: str
