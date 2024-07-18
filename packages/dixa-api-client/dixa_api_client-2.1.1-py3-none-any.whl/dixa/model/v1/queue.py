from typing import Literal, Required, TypedDict

from .bulk_action import BulkActionFailure
from .conversation import Channel


class Queue(TypedDict, total=False):
    id: Required[str]
    queuedAt: str


type MemberListType = Literal["Default", "SkillBased"]

type OfferingAlgorithm = Literal[
    "AgentPriorityOneAtATimeRandom",
    "AllAtOnce",
    "AgentPriorityLongestIdle",
    "AgentPriorityAllAtOnce",
    "LongestIdle",
    "OneAtATimeRandom",
]

type QueueThreshold = Literal[
    "SlaTimeLimit",
    "AvailableAgents",
    "LongestWait",
    "SlaPercentage",
    "WaitingConversations",
]

type SLACalculationMethod = Literal["AbandonedIgnored"]


class QueueUsages(TypedDict):
    queueId: str
    usages: dict[Channel, list[str]]


class Queue1(TypedDict, total=False):
    doNotOfferTimeouts: Required[dict[Channel, int]]
    id: Required[str]
    isDefault: Required[bool]
    isDoNotOfferEnabled: Required[bool]
    isPreferredAgentEnabled: bool
    memberListType: MemberListType
    name: Required[str]
    offerAbandonedConversations: bool
    offeringAlgorithm: OfferingAlgorithm
    offerTimeout: int
    organizationId: Required[str]
    personalAgentOfflineTimeout: int
    preferredAgentOfflineTimeout: int
    preferredAgentTimeouts: dict[Channel, int]
    priority: int
    queueThresholds: dict[QueueThreshold, int]
    slaCalculationMethod: SLACalculationMethod
    usages: QueueUsages
    wrapupTimeout: int


class AssignAgentBulkActionSuccess(TypedDict):
    data: str
    _type: Literal["BulkActionSuccess"]


type AssignAgentOutcome = BulkActionFailure | AssignAgentBulkActionSuccess

AssignAgentOutcomes = [BulkActionFailure, AssignAgentBulkActionSuccess]


class QueueMember(TypedDict, total=False):
    agentId: Required[str]
    priority: int
