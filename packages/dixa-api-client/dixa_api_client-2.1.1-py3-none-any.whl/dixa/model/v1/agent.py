from typing import Literal, Required, TypedDict

from .bulk_action import BulkActionFailure


class Agent(TypedDict, total=False):
    """Agent"""

    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    createdAt: Required[str]
    displayName: Required[str]
    email: Required[str]
    firstName: str
    id: Required[str]
    lastName: str
    middleNames: list[str]
    phoneNumber: str
    roles: list[str]


type ConnectionStatus = Literal["Online", "Offline"]

type PresenceStatus = Literal["Away", "Working"]


class AgentPresence(TypedDict, total=False):
    """AgentPresence"""

    activeChannels: list[str]
    connectionStatus: Required[ConnectionStatus]
    lastSeen: str
    presenceStatus: PresenceStatus
    requestTime: Required[str]
    userId: Required[str]


type AgentBulkActionOutcome = AgentBulkActionSuccess | BulkActionFailure


class AgentBulkActionSuccess(TypedDict):
    data: list[Agent]
    _type: Literal["BulkActionSuccess"]


AgentBulkActionOutcomes = [AgentBulkActionSuccess, BulkActionFailure]
