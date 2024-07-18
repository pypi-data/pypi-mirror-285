from typing import Required, TypedDict


class EmailEndpoint(TypedDict, total=False):
    address: Required[str]
    name: str
    senderOverride: str


class TelephonyEndpoint(TypedDict, total=False):
    functionality: list[str]
    name: str
    number: Required[str]


type ContactEndpoint = EmailEndpoint | TelephonyEndpoint

ContactEndpoints = [EmailEndpoint, TelephonyEndpoint]
