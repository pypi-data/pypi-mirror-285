from typing import Literal, Required, TypedDict

from .bulk_action import BulkActionFailure


class EndUserCustomAttribute(TypedDict):
    id: str
    identifier: str
    name: str
    value: list[str]


class EndUser(TypedDict, total=False):
    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    createdAt: Required[str]
    customAttributes: list[EndUserCustomAttribute]
    displayName: str
    email: str
    externalId: str
    firstName: str
    id: Required[str]
    lastName: str
    middleNames: list[str]
    phoneNumber: str


class EndUserPatchBulkActionSuccess(TypedDict):
    data: EndUser
    _type: Literal["BulkActionSuccess"]


type EndUserPatchBulkActionOutcome = EndUserPatchBulkActionSuccess | BulkActionFailure

EndUserPatchBulkActionOutcomes = [EndUserPatchBulkActionSuccess, BulkActionFailure]
