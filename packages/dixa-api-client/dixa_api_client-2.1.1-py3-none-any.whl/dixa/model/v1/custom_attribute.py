from typing import Literal, Optional, TypedDict


class SelectOption(TypedDict):
    id: str
    isDeactivated: bool
    label: str
    nestedOptions: Optional[list[dict]]
    value: str


SelectOption.__annotations__["nestedOptions"] = Optional[list[SelectOption]]


class Select(TypedDict):
    id: str
    isDeactivated: bool
    label: str
    nestedOptions: Optional[list[SelectOption]]
    value: str


class Text1(TypedDict, total=False):
    placeholder: str


class CustomAttributeInputDefinition(TypedDict):
    options: Select | Text1


class CustomAttributeDefinition(TypedDict):
    createdAt: str
    description: str
    entityType: Literal["Contact", "Conversation"]
    id: str
    identifier: str
    inputDefinition: CustomAttributeInputDefinition
    isArchived: bool
    isDeactivated: bool
    isRequired: bool
    label: str
    updatedAt: Optional[str]
