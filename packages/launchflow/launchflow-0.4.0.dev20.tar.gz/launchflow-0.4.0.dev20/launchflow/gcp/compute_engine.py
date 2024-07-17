# Handling imports and missing dependencies
try:
    import redis
except ImportError:
    redis = None
try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import pg8000
except ImportError:
    pg8000 = None

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from sqlalchemy.ext.asyncio import create_async_engine
except ImportError:
    async_sessionmaker = None
    create_async_engine = None

try:
    from sqlalchemy import create_engine, text
except ImportError:
    create_engine = None
    text = None
    DeclarativeBase = None


import dataclasses
from typing import Dict, List, Optional

from launchflow import exceptions
from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Inputs, Outputs
from launchflow.resource import T, TofuInputs
from launchflow.utils import generate_random_password


def _check_redis_installs():
    if redis is None:
        raise ImportError(
            "redis library is not installed. Please install it with `pip install redis`."
        )


# Every Compute Engine resource has some common attributes as well as additional outputs that are resource-specific.
@dataclasses.dataclass
class ComputeEngineBaseOutputs(Outputs):
    vm_ip: str
    ports: List[int]
    additional_outputs: Dict[str, str]


@dataclasses.dataclass
class ComputeEngineRedisAdditionalOutputs(Outputs):
    password: str
    redis_port: str


@dataclasses.dataclass
class ComputeEngineRedisOutputs(ComputeEngineBaseOutputs):
    additional_outputs: ComputeEngineRedisAdditionalOutputs


@dataclasses.dataclass
class ComputeEnginePostgresAdditionalOutputs(Outputs):
    password: str
    postgres_port: str


@dataclasses.dataclass
class ComputeEnginePostgresOutputs(ComputeEngineBaseOutputs):
    additional_outputs: ComputeEnginePostgresAdditionalOutputs


@dataclasses.dataclass
class EnvironmentVariable(Inputs):
    name: str
    value: str


@dataclasses.dataclass
class DockerConfig(Inputs):
    image: str
    args: List[str]
    environment_variables: List[EnvironmentVariable]


@dataclasses.dataclass
class FirewallConfig(Inputs):
    expose_ports: List[int]


@dataclasses.dataclass
class VMConfig(TofuInputs):
    additional_outputs: Dict[str, str]
    docker_cfg: DockerConfig
    machine_type: Optional[str] = None
    firewall_cfg: Optional[FirewallConfig] = None


class ComputeEngine(GCPResource[T]):
    """A Compute Engine VM running a Docker container.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://cloud.google.com/compute/docs/).

    ### Example Usage
    ```python
    import launchflow as lf

    # Automatically creates / connects to a Compute Engine VM with a provided Docker image
    compute_engine = lf.gcp.ComputeEngine("my-compute-engine", vm_config=lf.gcp.compute_engine.VMConfig(
        additional_outputs={"my_output": "my_value"},
        docker_cfg=lf.gcp.compute_engine.DockerConfig(
            image="my-docker-image",
            args=[],
            environment_variables=[lf.gcp.compute_engine.EnvironmentVariable("MY_ENV_VAR": "my_value")],
        ),
        firewall_cfg=lf.gcp.compute_engine.FirewallConfig(expose_ports=[80]),
    ))
    ```

    ### Arguments
    - `vm_config` (VMConfig): The configuration for the VM.
        - `additional_outputs` (dict): Additional outputs to be returned by the resource.
        - `docker_cfg` (DockerConfig): The configuration for the Docker container.
            - `image` (str): The Docker image to run.
            - `args` (List[str]): The arguments to pass to the Docker container.
            - `environment_variables` (List[EnvironmentVariable]): Environment variables to set in the Docker container.
        - `firewall_cfg` (FirewallConfig): The configuration for the firewall rules.
            - `expose_ports` (List[int]): The ports to expose in the firewall.

    """

    product = ResourceProduct.GCP_COMPUTE_ENGINE

    def __init__(self, name: str, vm_config: Optional[VMConfig]) -> None:
        """Create a Compute Engine resource.
        **Args**:
        - `name` (str): The name of the resource. This must be globally unique.
        - `vm_config` (VMConfig): The configuration for the VM.
            - `additional_outputs` (dict): Additional outputs to be returned by the resource.
            - `docker_cfg` (DockerConfig): The configuration for the Docker container.
                - `image` (str): The Docker image to run.
                - `args` (List[str]): The arguments to pass to the Docker container.
                - `environment_variables` (List[EnvironmentVariable]): Environment variables to set in the Docker container.
            - `firewall_cfg` (FirewallConfig): The configuration for the firewall rules.
                - `expose_ports` (List[int]): The ports to expose in the firewall.
        """
        super().__init__(
            name=name,
        )
        self.vm_config = vm_config

    def inputs(self, environment_type: EnvironmentType) -> VMConfig:
        if self.vm_config is None:
            raise ValueError("VM configuration is required.")
        if self.vm_config.machine_type is not None:
            return self.vm_config
        if environment_type == EnvironmentType.PRODUCTION:
            machine_type = "n1-standard-1"
        else:
            machine_type = "f1-micro"
        return dataclasses.replace(self.vm_config, machine_type=machine_type)


class ComputeEnginePostgres(ComputeEngine[ComputeEnginePostgresOutputs]):
    """A Postgres instance running on a VM in Google Compute Engine.

    **Example usage**:
    ```python
    from sqlalchemy import text
    import launchflow as lf

    postgres_compute_engine = lf.gcp.ComputeEnginePostgres("ce-postgres-mn-test-2")
    engine = postgres_compute_engine.sqlalchemy_engine()

    with engine.connect() as connection:
        print(connection.execute(text("SELECT 1")).fetchone())  # prints (1,)
    ```
    """

    def __init__(self, name: str, *, password: Optional[str] = None) -> None:
        """Create a new Compute Engine Postgres resource.

        **Args**:
        - `name` (str): The name of the Postgres VM resource. This must be globally unique.
        - `password` (str): The password for the Postgres DB. If not provided, a random password will be generated.
        """
        super().__init__(name=name, vm_config=None)
        self.password = password

    def inputs(self, environment_type: EnvironmentType) -> VMConfig:
        if self.password is None:
            try:
                # Attempt to see if the resource exists yet
                password = self.outputs().additional_outputs.password
            except exceptions.ResourceOutputsNotFound:
                password = generate_random_password()
        else:
            password = self.password
        self.vm_config = VMConfig(
            resource_id=self.resource_id,
            additional_outputs={"postgres_port": "5432", "password": password},
            docker_cfg=DockerConfig(
                image="postgres:latest",
                args=[],
                environment_variables=[
                    EnvironmentVariable("POSTGRES_PASSWORD", password)
                ],
            ),
            firewall_cfg=FirewallConfig(expose_ports=[5432]),
        )
        return super().inputs(environment_type)

    def query(self, query: str):
        """Executes a SQL query on the Postgres instance running on the Compute Engine VM.

        Args:
        - `query`: The SQL query to execute.

        **Example usage:**
        ```python
        import launchflow as lf

        postgres = lf.gcp.ComputeEnginePostgres("my-pg-db")

        # Executes a query on the Postgres instance running on the Compute Engine VM
        postgres.query("SELECT 1")
        ```

        **NOTE**: This method is not recommended for production use. Use `sqlalchemy_engine` instead.
        """
        engine = self.sqlalchemy_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            connection.commit()
            if result.returns_rows:
                return result.fetchall()

    def django_settings(self):
        if psycopg2 is None:
            raise ImportError(
                "psycopg2 is not installed. Please install it with `pip install psycopg2`."
            )

        connection_info = self.outputs()
        return {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": connection_info.additional_outputs.password,
            "HOST": connection_info.vm_ip,
            "PORT": connection_info.additional_outputs.postgres_port,
        }

    def sqlalchemy_engine_options(self):
        if pg8000 is None:
            raise ImportError(
                "pg8000 is not installed. Please install it with `pip install pg8000`."
            )

        connection_info = self.outputs()
        return {
            "url": f"postgresql+pg8000://postgres:{connection_info.additional_outputs.password}@{connection_info.vm_ip}:{connection_info.additional_outputs.postgres_port}/postgres",
        }

    async def sqlalchemy_async_engine_options(self):
        if asyncpg is None:
            raise ImportError(
                "asyncpg is not installed. Please install it with `pip install asyncpg`."
            )

        connection_info = await self.outputs_async()
        return {
            "url": f"postgresql+asyncpg://postgres:{connection_info.additional_outputs.password}@{connection_info.vm_ip}:{connection_info.additional_outputs.postgres_port}/postgres"
        }

    def sqlalchemy_engine(self, **engine_kwargs):
        """Returns a SQLAlchemy engine for connecting to a postgres instance hosted on GCP compute engine.

        Args:
        - `**engine_kwargs`: Additional keyword arguments to pass to `sqlalchemy.create_engine`.

        **Example usage:**
        ```python
        import launchflow as lf
        db = lf.gcp.ComputeEnginePostgres("my-pg-db")
        engine = db.sqlalchemy_engine()
        ```
        """
        if create_engine is None:
            raise ImportError(
                "SQLAlchemy is not installed. Please install it with "
                "`pip install sqlalchemy`."
            )

        engine_options = self.sqlalchemy_engine_options()
        engine_options.update(engine_kwargs)

        return create_engine(**engine_options)

    async def sqlalchemy_async_engine(self, **engine_kwargs):
        """Returns an async SQLAlchemy engine for connecting to a postgres instance hosted on GCP compute engine.

        Args:
        - `**engine_kwargs`: Additional keyword arguments to pass to `create_async_engine`.

        **Example usage:**
        ```python
        import launchflow as lf
        db = lf.gcp.ComputeEnginePostgres("my-pg-db")
        engine = await db.sqlalchemy_async_engine()
        ```
        """
        if create_async_engine is None:
            raise ImportError(
                "SQLAlchemy asyncio extension is not installed. "
                "Please install it with `pip install sqlalchemy[asyncio]`."
            )

        engine_options = await self.sqlalchemy_async_engine_options()
        engine_options.update(engine_kwargs)

        return create_async_engine(**engine_options)


class ComputeEngineRedis(ComputeEngine[ComputeEngineRedisOutputs]):
    """A Redis resource running on a VM in Google Compute Engine.

    **Args**:
    - `name` (str): The name of the Redis VM resource. This must be globally unique.
    - `password` (str): The password for the Redis DB. If not provided, a random password will be generated.

    **Example usage:**
    ```python
    import launchflow as lf

    redis = lf.gcp.ComputeEngineRedis("my-redis-instance")

    # Set a key-value pair
    client = redis.redis()
    client.set("my-key", "my-value")

    # Async compatible
    async_client = await redis.redis_async()
    await async_client.set("my-key", "my-value")
    ```
    """

    def __init__(self, name: str, *, password: Optional[str] = None) -> None:
        super().__init__(name=name, vm_config=None)
        self.password = password
        self._async_pool = None
        self._sync_client = None

    def inputs(self, environment_type: EnvironmentType) -> VMConfig:
        if self.password is None:
            try:
                # Attempt to see if the resource exists yet
                password = self.outputs().additional_outputs.password
            except exceptions.ResourceOutputsNotFound:
                password = generate_random_password()
        else:
            password = self.password
        self.vm_config = VMConfig(
            resource_id=self.resource_id,
            additional_outputs={"redis_port": "6379", "password": password},
            docker_cfg=DockerConfig(
                image="redis:latest",
                args=f"redis-server --appendonly yes --requirepass {password}".split(),
                environment_variables=[],
            ),
            firewall_cfg=FirewallConfig(expose_ports=[6379]),
        )
        return super().inputs(environment_type)

    def django_settings(self):
        connection_info = self.outputs()
        return {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": f"redis://default:{connection_info.additional_outputs.password}@{connection_info.vm_ip}:{connection_info.additional_outputs.redis_port}",
        }

    def redis(self, *, decode_responses: bool = True):
        """Get a Generic Redis Client object from the redis-py library.

        **Returns**:
        - The [Generic Redis Client](https://redis-py.readthedocs.io/en/stable/connections.html#generic-client) from the redis-py library.
        """
        _check_redis_installs()
        connection_info = self.outputs()
        if self._sync_client is None:
            self._sync_client = redis.Redis(
                host=connection_info.vm_ip,
                port=int(connection_info.additional_outputs.redis_port),
                password=connection_info.additional_outputs.password,
                decode_responses=decode_responses,
            )
        return self._sync_client

    async def redis_async(self, *, decode_responses: bool = True):
        """Get an Async Redis Client object from the redis-py library.

        **Returns**:
        - The [Async Redis Client object](https://redis-py.readthedocs.io/en/stable/connections.html#async-client) from the redis-py library.
        """
        _check_redis_installs()
        connection_info = await self.outputs_async()
        if self._async_pool is None:
            self._async_pool = await redis.asyncio.from_url(
                f"redis://{connection_info.vm_ip}:{connection_info.additional_outputs.redis_port}",
                password=connection_info.additional_outputs.password,
                decode_responses=decode_responses,
            )
        return self._async_pool
