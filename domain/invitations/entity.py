from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel


class InvitationStatus(StrEnum):
    CREATED = "CREATED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class InvitationDestinationType(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    USER_ID = "USER_ID"


class Invitation(BaseModel):
    id: str
    event_id: str
    inviter_id: str
    ticket_id: str | None = None
    name: str
    destination: str
    destination_type: InvitationDestinationType
    status: InvitationStatus
    expires_at: str
    created_at: str
    updated_at: str
    guest_slot_count: int = 0
    metadata: dict = {}


class InvitationQueryParams(BaseModel):
    event_id: str | None = None
    inviter_id: str | None = None
    status: InvitationStatus | None = None
    limit: int | None = None
    offset: int | None = None
    tag_id: str | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("event_id", "event_id", "=="),
        ("inviter_id", "inviter_id", "=="),
        ("status", "status", "=="),
    ]
