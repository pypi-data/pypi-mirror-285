try:
    from google.cloud.pubsub import PublisherClient
    from google.pubsub_v1.services.publisher import PublisherAsyncClient
    from google.pubsub_v1.types import PubsubMessage
except ImportError:
    PublisherClient = None
    PublisherAsyncClient = None
    PubsubMessage = None


import dataclasses
import datetime
from typing import Dict, Optional, Union

from launchflow.gcp.resource import GCPResource
from launchflow.models.enums import EnvironmentType, ResourceProduct
from launchflow.models.flow_state import EnvironmentState
from launchflow.node import Inputs, Outputs
from launchflow.resource import TofuInputs


@dataclasses.dataclass
class PubsubTopicOutputs(Outputs):
    topic_id: str


@dataclasses.dataclass
class PubsubTopicInputs(TofuInputs):
    message_retention_duration: Optional[str]


class PubsubTopic(GCPResource[PubsubTopicOutputs]):
    """A GCP Cloud Pub/Sub Topic.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://cloud.google.com/pubsub/docs/overview).

    ## Example Usage
    ```python
    import launchflow as lf

    # Automatically creates / connects to a PubSub Topic in your GCP project
    topic = lf.gcp.PubsubTopic("my-pubsub-topic")

    topic.publish(b"Hello, world!")
    ```

    ## Utility Methods
    """

    product = ResourceProduct.GCP_PUBSUB_TOPIC

    def __init__(
        self, name: str, message_retention_duration: Optional[datetime.timedelta] = None
    ) -> None:
        super().__init__(name=name)
        if message_retention_duration is not None:
            if message_retention_duration > datetime.timedelta(days=31):
                raise ValueError(
                    "Message retention duration must be less than or equal to 31 days."
                )
            if message_retention_duration < datetime.timedelta(minutes=10):
                raise ValueError(
                    "Message retention duration must be greater than or equal to 10 minutes."
                )
        self.message_retention_duration = message_retention_duration

    def import_resource(self, environment: EnvironmentState) -> Dict[str, str]:
        return {"google_pubsub_topic.topic": self.name}

    def inputs(self, environment_type: EnvironmentType) -> PubsubTopicInputs:
        if self.message_retention_duration is not None:
            duration_str = f"{int(self.message_retention_duration.total_seconds())}s"
        else:
            duration_str = None
        return PubsubTopicInputs(
            resource_id=self.resource_id, message_retention_duration=duration_str
        )

    def publish(self, data: bytes, ordering_key: str = ""):
        """Publish a message to the topic.

        Args:
        - `data`: The bytes to publish in the message
        - `ordering_key`: An optional ordering key for the message

        **Example usage:**

        ```python
        import launchflow as lf

        topic = lf.gcp.PubsubTopic("my-pubsub-topic")

        topic.publish(b"Hello, world!")
        ```
        """
        if PublisherClient is None:
            raise ImportError(
                "google-cloud-pubsub not installed. Please install it with "
                "`pip install launchflow[gcp]`."
            )
        connection = self.outputs()
        client = PublisherClient()
        return client.publish(connection.topic_id, data, ordering_key=ordering_key)

    async def publish_async(self, data: bytes, ordering_key: str = ""):
        """Asynchronously publish a message to the topic.

        Args:
        - `data`: The bytes to publish in the message
        - `ordering_key`: An optional ordering key for the message

        **Example usage:**

        ```python
        import launchflow as lf

        topic = lf.gcp.PubsubTopic("my-pubsub-topic")

        await topic.publish_async(b"Hello, world!")
        ```
        """
        if PublisherAsyncClient is None:
            raise ImportError(
                "google-cloud-pubsub not installed. Please install it with "
                "`pip install launchflow[gcp]`."
            )
        connection = await self.outputs_async()
        client = PublisherAsyncClient()
        return await client.publish(
            messages=[PubsubMessage(data=data, ordering_key=ordering_key)],
            topic=connection.topic_id,
        )


@dataclasses.dataclass
class OidcToken(Inputs):
    service_account_email: str
    audience: Optional[str] = None


@dataclasses.dataclass
class PushConfig(Inputs):
    push_endpoint: str
    oidc_token: Optional[OidcToken] = None
    attributes: Optional[Dict[str, str]] = None


@dataclasses.dataclass
class PubsubSubscriptionInputs(TofuInputs):
    topic: str
    push_config: Optional[PushConfig]
    ack_deadline_seconds: int
    message_retention_duration: str
    retain_acked_messages: bool
    filter: Optional[str]


@dataclasses.dataclass
class PubsubSubscriptionOutputs(Outputs):
    subscription_id: str


class PubsubSubscription(GCPResource[PubsubSubscriptionOutputs]):
    """A GCP Cloud Pub/Sub Subscription.

    Like all [Resources](/docs/concepts/resources), this class configures itself across multiple [Environments](/docs/concepts/environments).

    For more information see [the official documentation](https://cloud.google.com/pubsub/docs/overview).

    ## Example Usage
    ```python
    import launchflow as lf

    # Automatically creates / connects to a PubSub Topic in your GCP project
    topic = lf.gcp.PubsubSubscription("my-pubsub-sub")
    ```

    ## Utility Methods
    """

    product = ResourceProduct.GCP_PUBSUB_SUBSCRIPTION

    # TODO: Add optional arguments for subscription settings
    def __init__(
        self,
        name: str,
        topic: Union[PubsubTopic, str],
        push_config: Optional[PushConfig] = None,
        ack_deadline_seconds: int = 10,
        message_retention_duration: datetime.timedelta = datetime.timedelta(days=7),
        retain_acked_messages: bool = False,
        filter: Optional[str] = None,
    ) -> None:
        depends_on = []
        if isinstance(topic, PubsubTopic):
            self.topic = topic.resource_id
            depends_on.append(topic)
        elif isinstance(topic, str):
            self.topic = topic
        else:
            # TODO: revisit this when we have generics
            raise ValueError("topic must be a PubsubTopic or a str")
        self.push_config = push_config
        self.ack_deadline_seconds = ack_deadline_seconds
        self.message_retention_duration = message_retention_duration
        self.retain_acked_messages = retain_acked_messages
        self.filter = filter
        super().__init__(
            name=name,
            depends_on=depends_on,
        )

    def import_resource(self, environment: EnvironmentState) -> Dict[str, str]:
        return {"google_pubsub_subscription.subscription": self.name}

    def inputs(self, environment_type: EnvironmentType) -> PubsubSubscriptionInputs:
        message_retention_duration = None
        if self.message_retention_duration is not None:
            message_retention_duration = (
                f"{int(self.message_retention_duration.total_seconds())}s"
            )
        return PubsubSubscriptionInputs(
            resource_id=self.resource_id,
            topic=self.topic,
            push_config=self.push_config,
            ack_deadline_seconds=self.ack_deadline_seconds,
            message_retention_duration=message_retention_duration,
            retain_acked_messages=self.retain_acked_messages,
            filter=self.filter,
        )
