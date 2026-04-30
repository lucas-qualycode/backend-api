from enum import StrEnum

from pydantic import BaseModel


class InvitationGuestSlotStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class InvitationGuestSlot(BaseModel):
    id: str
    invitation_id: str
    first_name: str
    required_field_ids: list[str]
    status: InvitationGuestSlotStatus
    created_at: str
    updated_at: str
