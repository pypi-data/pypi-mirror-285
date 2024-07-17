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
    text = None
    create_engine = None
    DeclarativeBase = None
    sessionmaker = None


import dataclasses
import os
import subprocess
from typing import Dict, List, Optional

from launchflow import exceptions
from launchflow.aws.resource import AWSResource
from launchflow.generic_clients import RedisClient
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Inputs, Outputs
from launchflow.resource import T, TofuInputs
from launchflow.utils import generate_random_password


def _check_redis_installs():
    if redis is None:
        raise ImportError(
            "redis library is not installed. Please install it with `pip install redis`."
        )


@dataclasses.dataclass
class EC2BaseOutputs(Outputs):
    private_key: str
    vm_ip: str
    ports: List[int]
    additional_outputs: Dict[str, str]


@dataclasses.dataclass
class EC2RedisAdditionalOutputs(Outputs):
    password: str
    redis_port: str


@dataclasses.dataclass
class EC2RedisOutputs(EC2BaseOutputs):
    additional_outputs: EC2RedisAdditionalOutputs


@dataclasses.dataclass
class EC2PostgresAdditionalOutputs(Outputs):
    password: str
    postgres_port: str


@dataclasses.dataclass
class EC2PostgresOutputs(EC2BaseOutputs):
    additional_outputs: EC2PostgresAdditionalOutputs


@dataclasses.dataclass
class DockerConfig(Inputs):
    image: str
    args: List[str]
    environment_variables: Dict[str, str]


@dataclasses.dataclass
class FirewallConfig(Inputs):
    expose_ports: List[int]


@dataclasses.dataclass
class VMConfig(TofuInputs):
    additional_outputs: Dict[str, str]
    docker_cfg: DockerConfig
    instance_type: Optional[str] = None
    firewall_cfg: Optional[FirewallConfig] = None
    disk_size_gb: Optional[int] = 8


class EC2(AWSResource[T]):
    """An EC2 instance running a Docker container.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://docs.aws.amazon.com/ec2/).

    ## Example Usage
    ```python
    import launchflow as lf

    # Automatically creates / connects to an ECS VM with a provided Docker image
    ec2_instance = lf.aws.EC2("my-instance", vm_config=lf.aws.ec2.VMConfig(
        additional_outputs={"my_output": "my_value"},
        docker_cfg=lf.aws.ec2.DockerConfig(
            image="my-docker-image",
            args=[],
            environment_variables={"MY_ENV_VAR": "my_value"},
        ),
        firewall_cfg=lf.aws.ec2.FirewallConfig(expose_ports=[80]),
    ))
    ```

    ### Arguments
    - `vm_config` (VMConfig): The configuration for the VM.
        - `additional_outputs` (dict): Additional outputs to be returned by the resource.
        - `docker_cfg` (DockerConfig): The configuration for the Docker container.
            - `image` (str): The Docker image to run.
            - `args` (List[str]): The arguments to pass to the Docker container.
            - `environment_variables` (dict): Environment variables to set in the Docker container.
        - `firewall_cfg` (FirewallConfig): The configuration for the firewall rules.
            - `expose_ports` (List[int]): The ports to expose in the firewall.

    ## Utility Methods
    """

    product = ResourceProduct.AWS_EC2

    def __init__(self, name: str, vm_config: Optional[VMConfig]) -> None:
        """Create a new EC2 resource.

        **Args**:
        - `name` (str): The name of the resource. This must be globally unique.
        - `vm_config` (VMConfig): The configuration for the VM.
            - `instance_type` (str): The type of machine to use. Defaults to `t3.micro` for development environments and `t3.medium` for production environments.
            - `additional_outputs` (dict): Additional outputs to be returned by the resource.
            - `docker_cfg` (DockerConfig): The configuration for the Docker container.
                - `image` (str): The Docker image to run.
                - `args` (List[str]): The arguments to pass to the Docker container.
                - `environment_variables` (dict): Environment variables to set in the Docker container.
            - `firewall_cfg` (FirewallConfig): The configuration for the firewall rules.
                - `expose_ports` (List[int]): The ports to expose in the firewall.
            - `disk_size_gb`: The size of the disk in GB. Defaults to 8.
        """
        super().__init__(
            name=name,
        )
        self.vm_config = vm_config

    def inputs(self, environment_type: EnvironmentType) -> VMConfig:
        if self.vm_config is None:
            raise ValueError("vm_config is required")
        if self.vm_config.instance_type is not None:
            return self.vm_config
        if environment_type == EnvironmentType.PRODUCTION:
            instance_type = "t3.medium"
        else:
            instance_type = "t3.micro"
        return dataclasses.replace(self.vm_config, instance_type=instance_type)

    def ssh(self):
        """Open an SSH session to the VM.

        **Example usage**:
        ```python
        import launchflow as lf

        vm = lf.aws.EC2("my-vm")
        vm.ssh()
        ```
        """

        connection_info = self.outputs()
        # Path to the temporary private key file
        key_path = f"/tmp/{self.name}_private_key.pem"

        try:
            # Write the private key to a temporary file
            with open(key_path, "w") as f:
                f.write(connection_info.private_key)

            # Make the file read-only for the user
            os.chmod(key_path, 0o400)

            # Build the SSH command
            command = f"ssh -i {key_path} ec2-user@{connection_info.vm_ip}"
            print("Executing SSH command. Please wait...")

            # Execute the SSH command. This will drop the user into the SSH session.
            subprocess.run(command, shell=True)

        finally:
            # Ensure the temporary file is deleted after the SSH session ends
            if os.path.exists(key_path):
                os.remove(key_path)
                print("Temporary private key file deleted.")


class EC2Postgres(EC2[EC2PostgresOutputs]):
    """An EC2 instance running Postgres on Docker.

    **Example usage:**
    ```python
    from sqlalchemy import text
    import launchflow as lf

    postgres = lf.aws.EC2Postgres("my-postgres-db")
    engine = postgres.sqlalchemy_engine()

    with engine.connect() as connection:
        print(connection.execute(text("SELECT 1")).fetchone())  # prints (1,)
    ```
    """

    def __init__(
        self,
        name: str,
        *,
        password: Optional[str] = None,
        instance_type: Optional[str] = None,
        disk_size_gb: int = 8,
    ) -> None:
        """Create a new EC2Postgres resource.

        **Args**:
        - `name`: The name of the Postgres VM resource. This must be globally unique.
        - `password`: The password for the Postgres DB. If not provided, a random password will be generated.
        - `instance_type`: The type of machine to use. Defaults to `t3.micro` for development environments and `t3.medium` for production environments.
        - `disk_size_gb`: The size of the disk in GB. Defaults to 8.
        """
        super().__init__(name=name, vm_config=None)
        self.password = password
        self.instance_type = instance_type
        self.disk_size_gb = disk_size_gb

    def inputs(self, environment_type: EnvironmentType):
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
                environment_variables={"POSTGRES_PASSWORD": password},
            ),
            instance_type=self.instance_type,
            disk_size_gb=self.disk_size_gb,
            firewall_cfg=FirewallConfig(expose_ports=[5432]),
        )
        return super().inputs(environment_type)

    def query(self, query: str):
        """Executes a SQL query on the Postgres instance running on the EC2 VM.

        Args:
        - `query`: The SQL query to execute.

        **Example usage:**
        ```python
        import launchflow as lf

        postgres = lf.aws.EC2Postgres("my-pg-db")

        # Executes a query on the Postgres instance running on the EC2 VM
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
        """Returns a SQLAlchemy engine for connecting to a postgres instance hosted on EC2.

        Args:
        - `**engine_kwargs`: Additional keyword arguments to pass to `sqlalchemy.create_engine`.

        **Example usage:**
        ```python
        import launchflow as lf
        db = lf.aws.EC2Postgres("my-pg-db")
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
        """Returns an async SQLAlchemy engine for connecting to a postgres instance hosted on EC2.

        Args:
        - `**engine_kwargs`: Additional keyword arguments to pass to `create_async_engine`.

        **Example usage:**
        ```python
        import launchflow as lf
        db = lf.aws.EC2Postgres("my-pg-db")
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


class EC2Redis(EC2[EC2RedisOutputs], RedisClient):
    """An EC2 instance running Redis on Docker.

    **Example usage:**
    ```python
    import launchflow as lf

    redis_vm = lf.aws.EC2Redis("my-redis-instance")

    # Set a key-value pair
    client = redis_vm.redis()
    client.set("my-key", "my-value")

    # Async compatible
    async_client = await redis_vm.redis_async()
    await async_client.set("my-key", "my-value")
    ```
    """

    def __init__(
        self,
        name: str,
        *,
        password: Optional[str] = None,
        instance_type: Optional[str] = None,
        disk_size_gb: int = 8,
    ) -> None:
        """Create a new EC2Redis resource.

        **Args**:
        - `name` (str): The name of the Redis VM resource. This must be globally unique.
        - `password` (str): The password for the Redis DB. If not provided, a random password will be generated.
        - `instance_type`: The type of machine to use. Defaults to `t3.micro` for development environments and `t3.medium` for production environments.
        - `disk_size_gb`: The size of the disk in GB. Defaults to 8.
        """
        super().__init__(name=name, vm_config=None)
        self.password = password
        self.instance_type = instance_type
        self.disk_size_gb = disk_size_gb
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
                environment_variables={},
            ),
            instance_type=self.instance_type,
            disk_size_gb=self.disk_size_gb,
            firewall_cfg=FirewallConfig(expose_ports=[6379]),
        )
        return super().inputs(environment_type)

    def django_settings(self):
        """Returns a Django settings dictionary for connecting to the Redis instance running on EC2.

        **Example usage:**
        ```python
        import launchflow as lf

        redis_vm = lf.aws.EC2Redis("my-redis-vm")

        # settings.py
        CACHES = {
            # Connect Django's cache backend to the Redis instance running on EC2
            "default": redis_vm.django_settings(),
        }
        ```
        """
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
                port=int(connection_info.redis_port),
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
