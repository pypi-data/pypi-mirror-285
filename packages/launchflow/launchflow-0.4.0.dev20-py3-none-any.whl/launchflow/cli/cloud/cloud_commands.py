import rich
import typer

import launchflow
from launchflow.backend import LaunchFlowBackend
from launchflow.cli.utyper import UTyper
from launchflow.config import config
from launchflow.flows.create_flows import create
from launchflow.gcp.launchflow_cloud_releaser import LaunchFlowCloudReleaser
from launchflow.managers.environment_manager import EnvironmentManager
from launchflow.models.enums import EnvironmentStatus

app = UTyper(help="Commands for interacting with LaunchFlow Cloud.")


@app.command()
async def connect(
    environment: str = typer.Argument(None, help="The environment to connect."),
):
    """Connect an environment to LaunchFlow.

    For GCP this will create a service account that will be able to deploy your services, and allow LaunchFlow Cloud to use the service account to trigger deployments.
    """

    if not isinstance(config.launchflow_yaml.backend, LaunchFlowBackend):
        typer.echo(
            f"Unsupported backend: {type(config.launchflow_yaml.backend)}. This command only supports LaunchFlow Cloud backends."
        )
        raise typer.Exit(1)

    manager = EnvironmentManager(
        project_name=config.launchflow_yaml.project,
        environment_name=environment,
        backend=config.launchflow_yaml.backend,
    )

    env = await manager.load_environment()

    if env.status != EnvironmentStatus.READY:
        typer.echo(
            f"Environment {environment} is not ready. Please ensure the enviroment is ready before connecting to LaunchFlow Cloud."
        )
        raise typer.Exit(1)

    rich.print("\nConnecting environment to LaunchFlow Cloud...")
    launchflow.environment = manager.environment_name
    if env.gcp_config is not None:
        resource = LaunchFlowCloudReleaser()
        await create(resource, environment_name=manager.environment_name, prompt=False)
        await resource.connect_to_launchflow()
    else:
        typer.echo(
            "LaunchFlow cloud only support connecting GCP environments at this time. AWS will be supported soon. Reach out to team@launchflow.com for more information."
        )
        raise typer.Exit(1)
