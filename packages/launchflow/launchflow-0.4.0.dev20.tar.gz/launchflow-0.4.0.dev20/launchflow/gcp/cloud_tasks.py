import dataclasses
import datetime
import json as _json
from typing import Dict, Optional

from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.node import Outputs
from launchflow.resource import TofuInputs

try:
    from google.cloud import tasks
except ImportError:
    tasks = None


@dataclasses.dataclass
class CloudTasksQueueOutputs(Outputs):
    queue_id: str


@dataclasses.dataclass
class CloudTasksQueueInputs(TofuInputs):
    location: Optional[str]


# TODO: add methods that automatically enqueue a task with
# the environment credentials
class CloudTasksQueue(GCPResource[CloudTasksQueueOutputs]):
    # TODO: clean up example
    """A GCP Cloud Tasks Queue.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://cloud.google.com/tasks/docs/).

    ## Example Usage
    ```python
    import launchflow as lf

    # Automatically creates / connects to a Cloud Tasks Queue in your GCP project
    queue = lf.gcp.CloudTasksQueue("my-queue")

    queue.enqueue("https://example.com/endpoint", json={"key": "value"})
    ```

    ## Optional Arguments
    - `location` (Optional[str]): The location of the queue. If None, the GCP project's default region is used. Defaults to None.

    ```python
    import launchflow as lf

    queue = lf.gcp.CloudTasksQueue("my-queue", location="us-central1")
    ```

    ## Utility Methods
    """

    product = ResourceProduct.GCP_CLOUD_TASKS_QUEUE

    def __init__(self, name: str, location: Optional[str] = None) -> None:
        super().__init__(
            name=name,
            replacement_arguments={"location"},
        )
        """Create a new CloudTasksQueue.

        Args:
        - `name` (str): The name of the Cloud Tasks Queue.
        - `location` (Optional[str]): The location of the queue. If None, the environments default region is used. Defaults to None.
        """
        self.location = location

    def inputs(self, environment_type: EnvironmentType) -> CloudTasksQueueInputs:
        return CloudTasksQueueInputs(
            resource_id=self.resource_id, location=self.location
        )

    def enqueue(
        self,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        json: Optional[Dict] = None,
        oauth_token: Optional[str] = None,
        oidc_token: Optional[str] = None,
        schedule_time: Optional[datetime.datetime] = None,
    ) -> "tasks.Task":
        """Enqueue a task in the Cloud Tasks queue.

        Args:
        - `url`: The url the task will call.
        - `method`: The HTTP method to use. Defaults to "POST".
        - `headers`: A dictionary of headers to include in the request.
        - `body`: The body of the request. Only one of `body` or `json` can be provided.
        - `json`: A dictionary to be serialized as JSON and sent as the body of the request. Only one of `body` or `json` can be provided.
        - `oauth_token`: An OAuth token to include in the request.
        - `oidc_token`: An OIDC token to include in the request.
        - `schedule_time`: Optional[datetime.datetime] = None,

        **Example usage:**
        ```python
        import launchflow as lf

        queue = lf.gcp.CloudTasksQueue("my-queue")

        queue.enqueue("https://example.com/endpoint", json={"key": "value"})
        ```
        """
        if tasks is None:
            raise ImportError(
                "google-cloud-tasks not installed. Please install it with "
                "`pip install launchflow[gcp]`."
            )
        if body is not None and json is not None:
            raise ValueError("Cannot provide both body and json")
        if body is None and json is not None:
            body = _json.dumps(json).encode("utf-8")
        info = self.outputs()
        client = tasks.CloudTasksClient()
        return client.create_task(
            parent=info.queue_id,
            task=tasks.Task(
                http_request=tasks.HttpRequest(
                    url=url,
                    http_method=method,
                    headers=headers,
                    body=body,
                    oauth_token=oauth_token,
                    oidc_token=oidc_token,
                ),
                schedule_time=schedule_time,
            ),
        )

    async def enqueue_async(
        self,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        json: Optional[Dict] = None,
        oauth_token: Optional[str] = None,
        oidc_token: Optional[str] = None,
        schedule_time: Optional[datetime.datetime] = None,
    ) -> "tasks.Task":
        """Enqueue a task in the Cloud Tasks queue.

        Args:
        - `url`: The url the task will call.
        - `method`: The HTTP method to use. Defaults to "POST".
        - `headers`: A dictionary of headers to include in the request.
        - `body`: The body of the request. Only one of `body` or `json` can be provided.
        - `json`: A dictionary to be serialized as JSON and sent as the body of the request. Only one of `body` or `json` can be provided.
        - `oauth_token`: An OAuth token to include in the request.
        - `oidc_token`: An OIDC token to include in the request.
        - `schedule_time`: The time to schedule the task for.

        **Example usage:**
        ```python
        import launchflow as lf

        queue = lf.gcp.CloudTasksQueue("my-queue")

        await queue.enqueue_async("https://example.com/endpoint", json={"key": "value"})
        ```
        """
        if tasks is None:
            raise ImportError(
                "google-cloud-tasks not installed. Please install it with "
                "`pip install launchflow[gcp]`."
            )
        if body is not None and json is not None:
            raise ValueError("Cannot provide both body and json")
        if body is None and json is not None:
            body = _json.dumps(json).encode("utf-8")
        info = await self.outputs_async()
        client = tasks.CloudTasksAsyncClient()
        return await client.create_task(
            parent=info.queue_id,
            task=tasks.Task(
                http_request=tasks.HttpRequest(
                    url=url,
                    http_method=method,
                    headers=headers,
                    body=body,
                    oauth_token=oauth_token,
                    oidc_token=oidc_token,
                ),
                schedule_time=schedule_time,
            ),
        )
