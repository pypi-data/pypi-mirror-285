import dataclasses
from typing import Optional

from launchflow.models.enums import EnvironmentType, ResourceProduct

try:
    import boto3
    from botocore.exceptions import NoRegionError
except ImportError:
    boto3 = None
    NoRegionError = None


import launchflow as lf
from launchflow import exceptions
from launchflow.node import Outputs
from launchflow.resource import Resource, TofuInputs


@dataclasses.dataclass
class SecretsManagerSecretOutputs(Outputs):
    secret_id: str


@dataclasses.dataclass
class SecretsManagerSecretInputs(TofuInputs):
    recovery_window_in_days: int


class SecretsManagerSecret(Resource[SecretsManagerSecretOutputs]):
    """A Secrets Manager Secret resource.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://docs.aws.amazon.com/secretsmanager/).


    ## Example Usage
    ```python
    import launchflow as lf

    # Automatically configures a SecretsManager Secret in your AWS account
    secret = lf.aws.SecretsManagerSecret("my-secret")
    # Get the latest version of the secret
    value = secret.version()
    ```

    ## Utility Methods
    """

    product = ResourceProduct.AWS_SECRETS_MANAGER_SECRET

    def __init__(self, name: str, *, recovery_window_in_days: int = 30) -> None:
        """Create a new Secrets Manager Secret resource.

        **Args:**
        - `name` (str): The name of the secret.
        - `recovery_window_in_days` (int): The number of days that AWS Secrets Manager waits before it can delete the secret. Defaults to 30 days. If 0 is provided, the secret can be deleted immediately.
        """
        super().__init__(name=name, resource_id=f"{name}-{lf.project}-{lf.environment}")
        self.recovery_window_in_days = recovery_window_in_days
        self._cached_versions = {}

    def inputs(self, environment_type: EnvironmentType) -> SecretsManagerSecretInputs:
        """Get the inputs for the Secrets Manager Secret resource.

        **Args:**
        - `environment_type` (EnvironmentType): The type of environment.

        **Returns:**
        - SecretsManagerSecretInputs: The inputs for the Secrets Manager Secret resource.
        """
        return SecretsManagerSecretInputs(
            self.resource_id, self.recovery_window_in_days
        )

    def version(
        self,
        version_id: Optional[str] = None,
        use_cache: bool = False,
        region: Optional[str] = None,
    ) -> str:
        """Get the secret version from the Secrets Manager.

        **Args:**
        - `version_id` (Optional[str]): The version of the secret to get. If not provided, the latest version is returned.
        - `use_cache` (bool): Whether to cache the value of the secret in memory. Defaults to False.
        - `region` (Optional[str]): The AWS region to use. If not provided, the default region is used.

        **Returns:**
        - The value associated with the secret version.

        **Example usage:**

        ```python
        import launchflow as lf

        secret = lf.aws.SecretsManagerSecret("my-secret")
        value = secret.version()
        ```
        """
        if use_cache and version_id in self._cached_versions:
            return self._cached_versions[version_id]
        if boto3 is None:
            raise ImportError(
                "boto3 not found. "
                "You can install it with pip install launchflow[aws]"
            )
        if NoRegionError is None:
            raise ImportError(
                "botocore not found. "
                "You can install it with pip install launchflow[aws]"
            )
        connection_info = self.outputs()
        try:
            sm = boto3.client("secretsmanager", region_name=region)
        except NoRegionError:
            raise exceptions.NoAWSRegionError()
        if version_id is None:
            value = sm.get_secret_value(SecretId=connection_info.secret_id)
        else:
            value = sm.get_secret_value(
                SecretId=connection_info.secret_id, VersionId=version_id
            )
        data = value["SecretString"]
        if use_cache:
            self._cached_versions[version_id] = data
        return data

    def add_version(self, payload: str, region: Optional[str] = None):
        """Adds a new version of the secret to the Secrets Manager.

        **Args:**
        - `payload` (str): The value to add to the secret.
        - `region` (Optional[str]): The AWS region to use. If not provided, the default region is used.

        **Example usage:**

        ```python
        import launchflow as lf

        secret = lf.aws.SecretsManagerSecret("my-secret")
        secret.add_version("my-new-value")
        ```
        """
        if boto3 is None:
            raise ImportError(
                "boto3 not found. "
                "You can install it with pip install launchflow[aws]"
            )
        if NoRegionError is None:
            raise ImportError(
                "botocore not found. "
                "You can install it with pip install launchflow[aws]"
            )
        connection_info = self.outputs()
        try:
            sm = boto3.client("secretsmanager", region_name=region)
        except NoRegionError:
            raise exceptions.NoAWSRegionError()
        sm.put_secret_value(SecretId=connection_info.secret_id, SecretString=payload)
