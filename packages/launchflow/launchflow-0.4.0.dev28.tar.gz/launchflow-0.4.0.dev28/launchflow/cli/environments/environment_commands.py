import logging
from typing import Optional

import beaupy
import rich
import typer

from launchflow import exceptions
from launchflow.cli.utils import OutputFormat, json_to_yaml, print_response
from launchflow.cli.utyper import UTyper
from launchflow.config import config
from launchflow.flows.environments_flows import (
    create_environment,
    delete_environment,
    get_environment,
)
from launchflow.managers.environment_manager import EnvironmentManager
from launchflow.managers.project_manager import ProjectManager
from launchflow.models.enums import CloudProvider, EnvironmentType
from launchflow.models.utils import (
    RESOURCE_PRODUCTS_TO_RESOURCES,
    SERVICE_PRODUCTS_TO_SERVICES,
)
from launchflow.validation import validate_environment_name

app = UTyper(help="Interact with your LaunchFlow environments.")


# def _get_project():
#     # project = config.project
#     # if project is None:
#     #     if config.credentials is None:
#     rich.print("[red]No project specified.[/red]")
#     rich.print("Please specify a project using one the following methods:")
#     rich.print(
#         "\t1. Run `lf init` to generate a launchflow.yaml (recommended for local backends)."
#     )
#     rich.print(
#         "\t2. Run `lf login` to connect to LaunchFlow Cloud (recommended for remote backends)."
#     )
#     rich.print("\t3. Pass the `--project` flag to this command.")
#     rich.print("\t4. Export a `LAUNCHFLOW_PROJECT` environment variable.\n")
#     raise typer.Exit(1)
#     try:
#         # NOTE: We first try using config.project so ENV variables are included
#         project = config.project

#     except exceptions.LaunchFlowYamlNotFound:
#         rich.print(
#             "[red]No `launchflow.yaml` file found in the current directory.[/red]"
#         )
#         rich.print("Please run `lf init` to create one.\n")
#         raise typer.Exit(1)


@app.command()
async def create(
    name: str = typer.Argument(None, help="The environment name."),
    env_type: Optional[EnvironmentType] = typer.Option(
        None, help="The environment type (`development` or `production`)."
    ),
    cloud_provider: Optional[CloudProvider] = typer.Option(
        None, help="The cloud provider."
    ),
    # GCP cloud provider options, this are used if you are importing an existing setup
    gcp_project_id: Optional[str] = typer.Option(
        None, help="The GCP project ID to import."
    ),
    gcs_artifact_bucket: Optional[str] = typer.Option(
        None, help="The GCS bucket to import.", hidden=True
    ),
    gcp_organization_name: Optional[str] = typer.Option(
        None,
        help="The GCP organization name (organization/XXXXXX) to place newly create GCP projects in. If not provided you will be prompted to select an organization.",
    ),
    gcp_service_account_email: Optional[str] = typer.Option(
        None, help="The GCP service account email to import for the environment."
    ),
    auto_approve: bool = typer.Option(
        False, "--auto-approve", "-y", help="Auto approve environment creation."
    ),
):
    """Create a new environment in the current project."""
    if (
        gcp_project_id
        or gcs_artifact_bucket
        or gcp_service_account_email
        or gcp_organization_name
    ):
        if cloud_provider is not None and cloud_provider != CloudProvider.GCP:
            rich.print(
                "[red]Error: GCP options can only be used with the GCP cloud provider. Add the `--cloud-provider=gcp` flag and try again.[/red]"
            )
            raise typer.Exit(1)
        cloud_provider = CloudProvider.GCP

    if name is None:
        if auto_approve:
            typer.echo(
                "Environment name is required when using the --auto-approve | -y flag."
            )
            raise typer.Exit(1)

        name = beaupy.prompt("What would you like to name your Environment?")
        while True:
            try:
                validate_environment_name(name)
                break
            except ValueError as e:
                reason = str(e)
                rich.print(f"[red]{reason}[/red]")
                name = beaupy.prompt("Please enter a new Environment name.")
    else:
        validate_environment_name(name)

    environment_manager = EnvironmentManager(
        # NOTE: We use config.project so ENV variables are included
        project_name=config.project,
        environment_name=name,
        backend=config.launchflow_yaml.backend,
    )
    try:
        environment = await create_environment(
            env_type,
            cloud_provider=cloud_provider,
            manager=environment_manager,
            gcp_project_id=gcp_project_id,
            gcs_artifact_bucket=gcs_artifact_bucket,
            gcp_organization_name=gcp_organization_name,
            environment_service_account_email=gcp_service_account_email,
            prompt=not auto_approve,
        )
    except Exception as e:
        logging.debug("Exception occurred: %s", e, exc_info=True)
        rich.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if environment is not None:
        print_response(
            "Environment",
            environment.model_dump(
                mode="json", exclude_defaults=True, exclude_none=True
            ),
        )


@app.command()
async def list(
    output_format: OutputFormat = typer.Option(
        "default", "--format", "-f", help="Output format"
    ),
    expand_contents: bool = typer.Option(
        False, "--expand", "-e", help="List resources and services in the environments"
    ),
):
    """List all environments in the current directory's project."""
    manager = ProjectManager(
        # NOTE: We use config.project so ENV variables are included
        project_name=config.project,
        backend=config.launchflow_yaml.backend,
    )
    try:
        envs = await manager.list_environments()
    except Exception as e:
        logging.debug("Exception occurred: %s", e, exc_info=True)
        rich.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if not envs:
        rich.print("[yellow]No environments found.[/yellow]")
        return

    if output_format == OutputFormat.YAML:
        output_dict = {}
        for name, env in envs.items():
            env_manager = manager.create_environment_manager(name)

            output_dict[name] = {}
            output_dict[name]["environment"] = env.model_dump(
                mode="json", exclude_defaults=True, exclude_none=True
            )

            if expand_contents:
                resources = await env_manager.list_resources()
                resources.update(await env_manager.list_docker_resources())
                services = await env_manager.list_services()

                output_dict[name]["resources"] = {
                    name: resource.model_dump(
                        mode="json", exclude_defaults=True, exclude_none=True
                    )
                    for name, resource in resources.items()
                }
                output_dict[name]["services"] = {
                    name: service.model_dump(
                        mode="json", exclude_defaults=True, exclude_none=True
                    )
                    for name, service in services.items()
                }

        print(json_to_yaml(output_dict))
    else:
        print("Environments:")
        for name, env in envs.items():
            env_manager = manager.create_environment_manager(name)

            if env.gcp_config is not None:
                prefix = "GCPEnvironment"
            elif env.aws_config is not None:
                prefix = "AWSEnvironment"
            else:
                prefix = "Environment"
            print(f"- {prefix}(name='{name}', status='{env.status.value}')")
            if expand_contents:
                resources = await env_manager.list_resources()
                resources.update(await env_manager.list_docker_resources())
                if resources:
                    print("  - Resources:")
                    for name, resource in resources.items():
                        resource_cls = RESOURCE_PRODUCTS_TO_RESOURCES[resource.product]
                        print(f"    - {resource_cls.__name__}(name='{name}')")

                services = await env_manager.list_services()
                if services:
                    print("  - Services:")
                    for name, service in services.items():
                        service_cls = SERVICE_PRODUCTS_TO_SERVICES[service.product]
                        print(f"    - {service_cls.__name__}(name='{name}')")


@app.command()
async def get(
    name: Optional[str] = typer.Argument(None, help="The environment name."),
    output_format: OutputFormat = typer.Option(
        "default", "--format", "-f", help="Output format"
    ),
    expand_contents: bool = typer.Option(
        False, "--expand", "-e", help="List resources and services in the environment"
    ),
):
    """Get information about a specific environment."""
    if name is None:
        ps_manager = ProjectManager(
            backend=config.launchflow_yaml.backend, project_name=config.project
        )
        name, _ = await get_environment(
            ps_manager,
            environment_name=name,
            prompt_for_creation=False,
        )
    environment_manager = EnvironmentManager(
        # NOTE: We use config.project so ENV variables are included
        project_name=config.project,
        environment_name=name,
        backend=config.launchflow_yaml.backend,
    )
    try:
        env = await environment_manager.load_environment()
    except Exception as e:
        logging.debug("Exception occurred: %s", e, exc_info=True)
        rich.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if output_format == OutputFormat.YAML:
        output_dict = {}

        output_dict = {}
        output_dict["environment"] = env.model_dump(
            mode="json", exclude_defaults=True, exclude_none=True
        )

        if expand_contents:
            resources = await environment_manager.list_resources()
            resources.update(await environment_manager.list_docker_resources())
            services = await environment_manager.list_services()

            output_dict["resources"] = {
                name: resource.model_dump(
                    mode="json", exclude_defaults=True, exclude_none=True
                )
                for name, resource in resources.items()
            }
            output_dict["services"] = {
                name: service.model_dump(
                    mode="json", exclude_defaults=True, exclude_none=True
                )
                for name, service in services.items()
            }

        print(json_to_yaml(output_dict))
    else:
        if env.gcp_config is not None:
            prefix = "GCPEnvironment"
        elif env.aws_config is not None:
            prefix = "AWSEnvironment"
        else:
            prefix = "Environment"
        print(f"{prefix}(name='{name}', status='{env.status.value}')")


@app.command()
async def delete(
    name: Optional[str] = typer.Argument(None, help="The environment name."),
    detach: bool = typer.Option(
        False,
        help="If true we will not clean up any of the cloud resources associated with the environment and will simply delete the record from LaunchFlow.",
    ),
    auto_approve: bool = typer.Option(
        False, "--auto-approve", "-y", help="Auto approve environment deletion."
    ),
):
    """Delete an environment."""
    if name is None:
        ps_manager = ProjectManager(
            backend=config.launchflow_yaml.backend, project_name=config.project
        )
        name, _ = await get_environment(
            ps_manager,
            environment_name=name,
            prompt_for_creation=False,
        )
    environment_manager = EnvironmentManager(
        # NOTE: We use config.project so ENV variables are included
        project_name=config.project,
        environment_name=name,
        backend=config.launchflow_yaml.backend,
    )
    try:
        await environment_manager.load_environment()
    except exceptions.EnvironmentNotFound:
        rich.print(f"[red]Environment '{name}' not found.[/red]")
        raise typer.Exit(1)
    try:
        await delete_environment(
            manager=environment_manager, detach=detach, prompt=not auto_approve
        )
    except Exception as e:
        logging.debug("Exception occurred: %s", e, exc_info=True)
        rich.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@app.command()
async def unlock(
    name: str = typer.Argument(..., help="The environment to unlock."),
    auto_approve: bool = typer.Option(
        False, "--auto-approve", "-y", help="Auto approve environment force unlock."
    ),
):
    """Force unlock an environment."""
    environment_manager = EnvironmentManager(
        # NOTE: We use config.project so ENV variables are included
        project_name=config.project,
        environment_name=name,
        backend=config.launchflow_yaml.backend,
    )
    if not auto_approve:
        rich.print(
            f"[yellow]Are you sure you want to force unlock environment '{name}'? This can lead to data corruption or conflicts.[/yellow]"
        )
        # TODO: Link to docs that explain what force unlock does
        if not beaupy.confirm("Force unlock environment?"):
            rich.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(0)

    try:
        await environment_manager.force_unlock_environment()
        rich.print(f"[green]Environment '{name}' force unlocked.[/green]")
    except exceptions.EntityNotLocked:
        rich.print(
            f"[yellow]Environment '{name}' is not locked. Nothing to unlock.[/yellow]"
        )
        raise typer.Exit(1)
    except Exception as e:
        logging.debug("Exception occurred: %s", e, exc_info=True)
        rich.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
