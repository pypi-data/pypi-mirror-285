from typing import Literal, Optional, TypedDict


class WebhookSubscription(TypedDict):
    createdAt: str
    createdBy: str
    enabled: bool
    headers: dict[str, str]
    id: str
    name: str
    secretKey: str
    subscribedEvents: Optional[list[str]]
    updatedAt: str
    updatedBy: str
    url: str


class DeliveryDetail(TypedDict):
    deliveryTimestamp: str
    responseCode: int
    responseText: str
    success: bool
    _type: Literal["DeliveryDetail"]


class NoRecentDelivery(TypedDict):
    _type: Literal["NoRecentDelivery"]


class EventDeliveryLog(TypedDict):
    deliveryDetail: DeliveryDetail
    payload: str


type DeliveryStatus = DeliveryDetail | NoRecentDelivery

type Event = Literal[
    "ConversationPending",
    "AgentUnbannedEnduser",
    "ConversationMessageAdded",
    "ConversationTagAdded",
    "AgentBannedIp",
    "ConversationAssigned",
    "ConversationPendingExpired",
    "ConversationTransferred",
    "ConversationEnqueued",
    "ConversationCreated",
    "ConversationUnassigned",
    "ConversationOpen",
    "ConversationAbandoned",
    "ConversationClosed",
    "ConversationNoteAdded",
    "AgentBannedEnduser",
    "ConversationEndUserReplaced",
    "AgentUnbannedIp",
    "ConversationTagRemoved",
    "ConversationRated",
]


class EventDeliveryStatus(TypedDict):
    deliveryStatus: DeliveryStatus
    event: Event


class BasicAuth(TypedDict):
    password: str
    username: str
    _type: Literal["BasicAuth"]


class NoAuth(TypedDict):
    _type: Literal["NoAuth"]


class TokenAuth(TypedDict):
    value: str
    _type: Literal["TokenAuth"]


type Authorization = BasicAuth | NoAuth | TokenAuth
