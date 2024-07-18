from typing import Literal, Optional, Required, TypedDict

type MessageAttributes = (
    CallRecordingAttributes
    | ChatAttributes
    | ContactFormAttributes
    | EmailAttributes
    | FacebookMessengerAttributes
    | GenericAttributes
    | PhoneAttributes
    | SmsAttributes
    | TwitterAttributes
    | WhatsAppAttributes
)


class Message(TypedDict):
    """Message data."""

    id: str
    authorId: str
    externalId: Optional[str]
    createdAt: str
    attributes: MessageAttributes


class Attachment(TypedDict):
    """Attachment data."""

    prettyName: str
    url: str


type Direction = Literal["Inbound", "Outbound"]


class CallRecordingAttributes(TypedDict):
    """Call recording attributes."""

    duration: Optional[int]
    recording: str
    _type: Literal["CallRecordingAttributes"]


class HtmlContent(TypedDict):
    value: str
    _type: Literal["Html"]


class TextContent(TypedDict):
    value: str
    _type: Literal["Text"]


type Content = HtmlContent | TextContent


class EmailContent(TypedDict):
    """Email content data."""

    content: Content


class EmailContact(TypedDict):
    """Email contact data."""

    email: str
    name: str


class File(TypedDict):
    """File data."""

    prettyName: str
    url: str


class ChatAttributes(TypedDict, total=False):
    attachments: list[Attachment]
    content: Content
    direction: Direction
    isAutomated: Required[bool]
    _type: Required[Literal["ChatAttributes"]]


ContactFormAttributes = TypedDict(
    "ContactFormAttributes",
    {
        "attachments": list[Attachment],
        "bcc": list[EmailContact],
        "cc": list[EmailContact],
        "deliveryFailureReason": str,
        "direction": Direction,
        "emailContent": EmailContent,
        "from": EmailContact,
        "inlineImages": list[File],
        "isAutoReply": Required[bool],
        "originalContentUrl": File,
        "replyDefaultToEmails": list[EmailContact],
        "to": list[EmailContact],
        "_type": Required[Literal["ContactFormAttributes"]],
    },
    total=False,
)

EmailAttributes = TypedDict(
    "EmailAttributes",
    {
        "attachments": list[Attachment],
        "bcc": list[EmailContact],
        "cc": list[EmailContact],
        "deliveryFailureReason": str,
        "direction": Direction,
        "emailContent": EmailContent,
        "from": Required[EmailContact],
        "inlineImages": list[File],
        "isAutoReply": Required[bool],
        "originalContentUrl": File,
        "replyDefaultToEmails": list[EmailContact],
        "to": list[EmailContact],
        "_type": Required[Literal["EmailAttributes"]],
    },
    total=False,
)


class FacebookMessengerAttributes(TypedDict, total=False):
    """Facebook Messenger attributes."""

    attachments: list[Attachment]
    content: Content
    direction: Direction
    _type: Required[Literal["FacebookMessengerAttributes"]]


class GenericAttributes(TypedDict, total=False):
    """Generic attributes."""

    attachments: list[Attachment]
    content: Content
    direction: Direction
    _type: Required[Literal["GenericAttributes"]]


PhoneAttributes = TypedDict(
    "PhoneAttributes",
    {
        "direction": Direction,
        "duration": int,
        "from": Required[str],
        "to": Required[str],
        "_type": Required[Literal["PhoneAttributes"]],
    },
    total=False,
)


class SmsAttributes(TypedDict, total=False):
    """SMS attributes."""

    attachments: list[Attachment]
    content: Content
    direction: Direction
    _type: Required[Literal["SmsAttributes"]]


class TwitterAttributes(TypedDict, total=False):
    """Twitter attributes."""

    attachments: list[Attachment]
    content: Content
    direction: Direction
    _type: Required[Literal["TwitterAttributes"]]


class WhatsAppAttributes(TypedDict, total=False):
    """WhatsApp attributes."""

    attachments: list[Attachment]
    content: Content
    direction: Direction
    _type: Required[Literal["WhatsAppAttributes"]]
