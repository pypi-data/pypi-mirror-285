from typing import Literal, Required, TypedDict


class Queue(TypedDict, total=False):
    id: Required[str]
    queuedAt: str


type Channel = Literal[
    "WhatsApp",
    "Voicemail",
    "WidgetChat",
    "FacebookMessenger",
    "Email",
    "PstnPhone",
    "Sms",
    "Twitter",
    "Chat",
    "Messenger",
]

type RatingStatus = Literal["Unscheduled", "Offered", "Rated", "Scheduled", "Cancelled"]

type RatingType = Literal["CSAT", "ThumbsUpOrDown"]


class ConversationRating(TypedDict, total=False):
    agentId: str
    conversationChannel: Required[Channel]
    id: Required[str]
    language: str
    ratingCommend: str
    ratingScore: int
    ratingStatus: Required[RatingStatus]
    ratingType: Required[RatingType]
    timestamps: Required[dict[str, str]]
    userId: Required[str]


class ConversationFlow(TypedDict):
    channel: Channel
    contactEndpointId: str
    id: str
    name: str


class ConversationCustomAttribute(TypedDict):
    id: str
    identifier: str
    name: str
    value: str | list[str]


class EmailForward(TypedDict):
    _type: Literal["EmailForward"]
    parentId: str


class FollowUp(TypedDict):
    _type: Literal["FollowUp"]
    parentId: str


class SideConversation(TypedDict):
    _type: Literal["SideConversation"]
    parentId: str


type ConversationLink = EmailForward | FollowUp | SideConversation

type ConversationState = Literal["AwaitingPending", "Pending", "Closed", "Open"]


class AnonymizedConversation(TypedDict, total=False):
    anonymizedAt: Required[str]
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    id: Required[str]
    link: ConversationLink
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["AnonymizedConversation"]


class Assignment(TypedDict):
    agentId: str
    assignedAt: str


class BrowserInfo(TypedDict, total=False):
    ipAddress: str
    name: Required[str]
    originatingUrl: str
    version: str


type Direction = Literal["Inbound", "Outbound"]


class ChatConversation(TypedDict, total=False):
    assignment: Assignment
    browserInfo: BrowserInfo
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    id: Required[str]
    language: str
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["ChatConversation"]


class ContactFormConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    fromEmail: Required[str]
    id: Required[str]
    integrationEmail: str
    language: str
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    subject: str
    toEmail: str
    _type: Literal["ContactFormConversation"]


class EmailConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    fromEmail: Required[str]
    id: Required[str]
    integrationEmail: str
    language: str
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    subject: str
    toEmail: Required[str]
    _type: Literal["EmailConversation"]


class FacebookMessengerConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    id: Required[str]
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["FacebookMessengerConversation"]


class GenericConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    fromContactPointId: str
    id: Required[str]
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    toContactPointId: str
    _type: Literal["GenericConversation"]


class MessengerConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    id: Required[str]
    language: str
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["MessengerConversation"]


class PstnPhoneConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    id: Required[str]
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["PstnPhoneConversation"]


class SmsConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    fromNumber: str
    id: Required[str]
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    toNumber: str
    _type: Literal["SmsConversation"]


type ConversationType = Literal["DirectMessage", "Tweet"]


class TwitterConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    contactPointTwitterId: str
    conversationType: Required[ConversationType]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    endUserTwitterId: str
    id: Required[str]
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["TwitterConversation"]


class WhatsAppConversation(TypedDict, total=False):
    assignment: Assignment
    channel: Required[Channel]
    createdAt: Required[str]
    customAttributes: list[ConversationCustomAttribute]
    direction: Direction
    id: Required[str]
    link: ConversationLink
    queue: Queue
    requesterId: Required[str]
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["WhatsAppConversation"]


class ConversationSearchInnerHit(TypedDict, total=False):
    highlights: dict[str, list[str]]
    id: Required[str]


class ConversationSearchHit(TypedDict, total=False):
    highlights: dict[str, list[str]]
    id: Required[str]
    innerHits: list[ConversationSearchInnerHit]


type Conversation = (
    AnonymizedConversation
    | ChatConversation
    | ContactFormConversation
    | EmailConversation
    | FacebookMessengerConversation
    | GenericConversation
    | MessengerConversation
    | PstnPhoneConversation
    | SmsConversation
    | TwitterConversation
    | WhatsAppConversation
)

ConversationTypes = [
    AnonymizedConversation,
    ChatConversation,
    ContactFormConversation,
    EmailConversation,
    FacebookMessengerConversation,
    GenericConversation,
    MessengerConversation,
    PstnPhoneConversation,
    SmsConversation,
    TwitterConversation,
    WhatsAppConversation,
]


class ConversationResponse(TypedDict):
    id: int
