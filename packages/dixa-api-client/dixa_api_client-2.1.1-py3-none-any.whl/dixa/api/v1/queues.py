from typing import Required, TypedDict

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.conversation import Channel
from dixa.model.v1.queue import (
    AssignAgentOutcome,
    AssignAgentOutcomes,
    OfferingAlgorithm,
    Queue1,
    QueueMember,
    QueueThreshold,
)


class QueueAssignBody(TypedDict):
    agentIds: list[str]


class QueueCreateRequest(TypedDict, total=False):
    callFunctionality: bool
    doNotOfferTimeouts: dict[Channel, int]
    isDefault: Required[bool]
    isDoNotOfferEnabled: Required[bool]
    isPreferredAgentEnabled: bool
    name: Required[str]
    offerAbandonedConversations: bool
    offerAlgorithm: OfferingAlgorithm
    offerTimeout: int
    personalAgentOfflineTimeout: int
    preferredAgentOfflineTimeout: int
    preferredAgentTimeouts: dict[Channel, int]
    priority: int
    queueThresholds: dict[QueueThreshold, int]
    wrapupTimeout: int


class QueueCreateBody(TypedDict, total=False):
    request: QueueCreateRequest


class QueueRemoveBody(TypedDict):
    agentIds: list[str]


class QueueResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/
    """

    resource = "queues"
    dixa_version: DixaVersion = "v1"

    def assign(self, queue_id: str, body: QueueAssignBody) -> list[AssignAgentOutcome]:
        """Assign agents
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/#tag/Queues/operation/patchQueuesQueueidMembers
        """
        data = self.client.patch(f"{self._url}/{queue_id}/members", body, list)
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        results = []
        for item in data:
            for return_cls in AssignAgentOutcomes:
                try:
                    results.append(return_cls(**item))
                    break
                except TypeError:
                    continue
            else:
                raise DixaAPIError(
                    f"Expected one of {AssignAgentOutcome}, got {type(data).__name__}"
                )
        return results

    def create(self, body: QueueCreateBody) -> Queue1:
        """Create a queue.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/#tag/Queues/operation/postQueues
        """
        data = self.client.post(self._url, body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Queue1(**data)

    def get(self, queue_id: str) -> Queue1:
        """Get a queue by id.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/#tag/Queues/operation/getQueuesQueueid
        """
        data = self.client.get(f"{self._url}/{queue_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Queue1(**data)

    def list_agents(self, queue_id: str) -> list[QueueMember]:
        """List agents.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/#tag/Queues/operation/getQueuesQueueidMembers
        """
        return self.client.paginate(f"{self._url}/{queue_id}/members")

    def list_(self) -> list[Queue1]:
        """List queues.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/#tag/Queues/operation/getQueues
        """
        return self.client.paginate(self._url)

    def remove(self, queue_id: str, body: QueueRemoveBody):
        """Remove agents.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Queues/#tag/Queues/operation/deleteQueuesQueueidMembers
        """
        return self.client.delete(f"{self._url}/{queue_id}/members", body)
