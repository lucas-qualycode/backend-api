from typing import ClassVar

from pydantic import BaseModel


class Invitation(BaseModel):
    id: str
    event_id: str
    inviter_id: str
    ticket_ids: list[str] = []
    type: str
    destination: str
    destination_type: str
    status: str
    token: str
    expires_at: str
    created_at: str
    updated_at: str
    metadata: dict = {}


class InvitationQueryParams(BaseModel):
    event_id: str | None = None
    inviter_id: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("event_id", "event_id", "=="),
        ("inviter_id", "inviter_id", "=="),
        ("status", "status", "=="),
    ]


class InvitationStatus:
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
