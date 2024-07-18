from typing import Literal, Required, TypedDict, Union

type ActivityLogType = Literal[
    "ConversationRatingScheduled",
    "ConversationOfferAccepted",
    "ConversationPending",
    "ConversationRatingUnscheduled",
    "ConversationOfferRejected",
    "ConversationEndUserReplaced",
    "NoteAdded",
    "FollowupExpired",
    "ConversationRated",
    "TagAdded",
    "ConversationOfferTimeout",
    "MessageAddedByCustomer",
    "ConversationCreatedByCustomer",
    "ConversationCreatedByAgent",
    "TransferFailed",
    "TransferSuccessful",
    "ConversationOffered",
    "ConversationUnassigned",
    "TagRemoved",
    "TransferInitiated",
    "ConversationClaimed",
    "ConversationReopened",
    "ConversationClosed",
    "ConversationLanguageUpdated",
    "FollowupAdded",
    "ConversationAutoreplySent",
    "ConversationReserved",
    "ConversationAssigned",
    "ConversationRatingOffered",
    "ConversationRatingCancelled",
    "MessageAddedByAgent",
    "FollowupRemoved",
]

type ActivityLogAttributes = Union[
    ConversationAssignedAttribute,
    ConversationAutoReplySentAttribute,
    ConversationClaimedAttribute,
    ConversationCreatedAttribute,
    ConversationEndUserReplacedAttribute,
    ConversationLanguageUpdatedAttribute,
    ConversationOfferedAttribute,
    ConversationRatedAttribute,
    ConversationRatingOfferedAttribute,
    ConversationRatingScheduledAttribute,
    ConversationReservedAttribute,
    ConversationTransferredAttribute,
    ConversationUnassignedAttribute,
    MessageAddedAttribute,
    NoteAddedAttribute,
    TagAddedAttribute,
    TagRemovedAttribute,
]


class ActivityLogUser(TypedDict, total=False):
    email: str
    id: Required[str]
    name: str
    phoneNumber: str


class ConversationAssignedAttribute(TypedDict, total=False):
    agentId: Required[str]
    agentName: str


class ConversationAutoReplySentAttribute(TypedDict):
    templateName: str


class ConversationClaimedAttribute(TypedDict, total=False):
    claimedFromLabel: str
    claimedFromType: str


class ConversationCreatedAttribute(TypedDict, total=False):
    subject: str


class ConversationEndUserReplacedAttribute(TypedDict):
    newUser: ActivityLogUser
    oldUser: ActivityLogUser


class ConversationLanguageUpdatedAttribute(TypedDict):
    language: str


class ConversationOfferedAttribute(TypedDict, total=False):
    agentNames: list[str]
    queueLabel: str


class ConversationRatedAttribute(TypedDict, total=False):
    agent: Required[ActivityLogUser]
    message: str
    score: int


class ConversationRatingOfferedAttribute(TypedDict):
    agent: ActivityLogUser
    user: ActivityLogUser


class ConversationRatingScheduledAttribute(TypedDict):
    ratingScheduledTime: str


class ConversationReservedAttribute(TypedDict):
    agent: ActivityLogUser
    queueId: str
    queueName: str
    reservationType: str
    validUntil: str


class ConversationTransferredAttribute(TypedDict, total=False):
    destinationId: Required[str]
    destinationLabel: str
    destinationType: Required[str]
    reason: str
    transferType: Required[str]


class ConversationUnassignedAttribute(TypedDict, total=False):
    agent: ActivityLogUser


class MessageAddedAttribute(TypedDict, total=False):
    avatarUrl: str
    fromEndpoint: str
    messageId: Required[str]


class NoteAddedAttribute(TypedDict, total=False):
    avatarUrl: str
    messageId: Required[str]


class TagAddedAttribute(TypedDict):
    tag: str


class TagRemovedAttribute(TypedDict):
    tag: str


class ActivityLog(TypedDict, total=False):
    _type: ActivityLogType
    activityTimestamp: str
    attributes: ActivityLogAttributes
    author: ActivityLogUser
    conversationId: Required[str]
    id: str
