from typing import ClassVar

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    name: str
    description: str | None = None
    location_id: str | None = None
    active: bool
    is_paid: bool
    is_online: bool
    imageURL: str | None = None
    deleted: bool
    created_at: str
    updated_at: str
    created_by: str
    last_updated_by: str
    guest_list_token: str | None = None


class EventQueryParams(BaseModel):
    name: str | None = None
    active: bool | None = None
    is_paid: bool | None = None
    is_online: bool | None = None
    deleted: bool | None = None
    created_by: str | None = None
    tag_id: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("name", "name", "=="),
        ("active", "active", "=="),
        ("is_paid", "is_paid", "=="),
        ("is_online", "is_online", "=="),
        ("deleted", "deleted", "=="),
        ("created_by", "created_by", "=="),
    ]
