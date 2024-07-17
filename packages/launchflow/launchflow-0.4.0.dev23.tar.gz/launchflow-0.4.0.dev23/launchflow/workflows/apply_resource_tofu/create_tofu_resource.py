import yaml

from launchflow import exceptions
from launchflow.gcp_clients import write_to_gcs
from launchflow.workflows.apply_resource_tofu.schemas import (
    ApplyResourceTofuInputs,
    ApplyResourceTofuOutputs,
)
from launchflow.workflows.commands.tf_commands import TFApplyCommand
from launchflow.workflows.utils import run_tofu


async def create_tofu_resource(inputs: ApplyResourceTofuInputs):
    state_prefix = inputs.launchflow_uri.tf_state_prefix(
        module=inputs.resource.product.value
    )
    lf_state_url = inputs.launchflow_uri.launchflow_tofu_state_url(
        lock_id=inputs.lock_id, module=inputs.resource.product.value
    )

    tf_vars = {}
    if inputs.gcp_env_config:
        tf_vars.update(
            {
                "gcp_project_id": inputs.gcp_env_config.project_id,
                "gcp_region": inputs.gcp_env_config.default_region,
                "resource_id": inputs.resource_id,
                "artifact_bucket": inputs.gcp_env_config.artifact_bucket,
                "environment_service_account_email": inputs.gcp_env_config.service_account_email,
                **inputs.resource.inputs,
            }
        )
    else:
        tf_vars.update(
            {
                "aws_account_id": inputs.aws_env_config.account_id,
                "aws_region": inputs.aws_env_config.region,
                "resource_id": inputs.resource_id,
                "artifact_bucket": inputs.aws_env_config.artifact_bucket,
                "env_role_name": inputs.aws_env_config.iam_role_arn.split("/")[-1],
                "vpc_id": inputs.aws_env_config.vpc_id,
                "launchflow_project": inputs.launchflow_uri.project_name,
                "launchflow_environment": inputs.launchflow_uri.environment_name,
                **inputs.resource.inputs,
            }
        )

    tf_apply_command = TFApplyCommand(
        tf_module_dir=f"workflows/tf/resources/{inputs.resource.product.value}",
        backend=inputs.backend,
        tf_state_prefix=state_prefix,
        tf_vars=tf_vars,
        logs_file=inputs.logs_file,
        launchflow_state_url=lf_state_url,
    )

    output = await run_tofu(tf_apply_command)

    # TODO: it would be nice if we could have some validation here
    output_key = f"resources/{inputs.launchflow_uri.resource_name}.yaml"
    yaml_data = yaml.safe_dump(output)
    if inputs.gcp_env_config is not None:
        await write_to_gcs(
            bucket=inputs.gcp_env_config.artifact_bucket,
            prefix=output_key,
            data=yaml_data,
        )
    if inputs.aws_env_config is not None:
        try:
            import boto3
        except ImportError:
            raise exceptions.MissingAWSDependency()
        client = boto3.client("s3")
        client.put_object(
            Bucket=inputs.aws_env_config.artifact_bucket,
            Key=output_key,
            Body=yaml_data,
        )

    return ApplyResourceTofuOutputs(
        gcp_id=output.get("gcp_id"), aws_arn=output.get("aws_arn")
    )
