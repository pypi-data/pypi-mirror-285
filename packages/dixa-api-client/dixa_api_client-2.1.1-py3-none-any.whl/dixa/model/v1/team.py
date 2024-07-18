from typing import Required, TypedDict


class Team(TypedDict):
    id: str


class Team1(TypedDict):
    id: str
    name: str


class TeamMember(TypedDict, total=False):
    email: str
    id: Required[str]
    name: str
    phoneNumber: str
