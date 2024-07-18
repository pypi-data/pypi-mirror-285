from typing import Literal, Required, TypedDict

type TagState = Literal["Active", "Inactive"]


class Tag(TypedDict, total=False):
    color: str
    id: Required[str]
    name: Required[str]
    state: Required[TagState]
