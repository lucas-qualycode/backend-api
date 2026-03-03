from typing import ClassVar

from pydantic import BaseModel


class Attendee(BaseModel):
    id: str
    event_id: str
    user_id: str
    user_product_id: str
    invitation_id: str | None = None
    status: str
    check_in_time: str | None = None
    created_at: str
    updated_at: str
    metadata: dict = {}


class AttendeeQueryParams(BaseModel):
    event_id: str | None = None
    user_id: str | None = None
    user_product_id: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("event_id", "event_id", "=="),
        ("user_id", "user_id", "=="),
        ("user_product_id", "user_product_id", "=="),
        ("status", "status", "=="),
    ]


class AttendeeStatus:
    REGISTERED = "REGISTERED"
    CHECKED_IN = "CHECKED_IN"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
