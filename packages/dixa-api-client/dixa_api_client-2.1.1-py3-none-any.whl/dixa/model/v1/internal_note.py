from typing import TypedDict


class InternalNote(TypedDict):
    """Internal Note"""

    authorId: str
    createdAt: str
    csid: int
    id: str
    message: str
