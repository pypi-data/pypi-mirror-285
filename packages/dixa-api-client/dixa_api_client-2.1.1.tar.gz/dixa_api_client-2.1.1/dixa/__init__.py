import logging

import dixa.api.v1 as v1
from dixa.client import DixaClient


class DixaV1:
    """Dixa API v1."""

    def __init__(self, client: DixaClient):
        """Initializes the Dixa API v1. Do not use this class directly."""
        self.Agent = v1.AgentResource(client)
        self.Analytics = v1.AnalyticsResource(client)
        self.ContactEndpoint = v1.ContactEndpointResource(client)
        self.Conversation = v1.ConversationResource(client)
        self.EndUser = v1.EndUserResource(client)
        self.Queue = v1.QueueResource(client)
        self.Tag = v1.TagResource(client)
        self.Team = v1.TeamResource(client)
        self.Webhook = v1.WebhookResource(client)


class Dixa:
    """Dixa API Client"""

    def __init__(
        self,
        api_key: str,
        api_secret: str | None = None,
        max_retries: int = 3,
        retry_delay: int = 10,
        logger: logging.Logger | None = None,
    ):
        """Initializes the Dixa API client."""

        self.client = DixaClient(api_key, api_secret, max_retries, retry_delay, logger)

        self.v1 = DixaV1(self.client)


__all__ = ["Dixa"]
