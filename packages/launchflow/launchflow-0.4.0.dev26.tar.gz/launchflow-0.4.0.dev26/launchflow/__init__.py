# ruff: noqa
import asyncio
from typing import List

from launchflow.config import config as lf_config
from launchflow.node import Outputs
from launchflow.resource import Resource

from . import aws, docker, fastapi, gcp, testing
from .flows.create_flows import create
from .flows.resource_flows import destroy

# TODO: Add generic resource imports, like Postgres, StorageBucket, etc.
# This should probably live directly under launchflow, i.e. launchflow/postgres.py


async def connect_all(*resources: Resource) -> List[Outputs]:
    connect_tasks = [resource.outputs_async() for resource in resources]
    return await asyncio.gather(*connect_tasks)


def is_deployment():
    return lf_config.env.deployment_id is not None


project = lf_config.project
environment = lf_config.environment

__version__ = "0.4.0.dev20"
