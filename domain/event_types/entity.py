from typing import ClassVar

from pydantic import BaseModel


class EventType(BaseModel):
    id: str
    name: str
    description: str | None = None
    active: bool
    deleted: bool
    created_at: str
    updated_at: str
    created_by: str
    last_updated_by: str


class EventTypeQueryParams(BaseModel):
    name: str | None = None
    active: bool | None = None
    deleted: bool | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("active", "active", "=="),
        ("deleted", "deleted", "=="),
    ]
