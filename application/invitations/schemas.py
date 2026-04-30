from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from domain.invitations.entity import InvitationDestinationType


class CreateInvitationGuestSlotInput(BaseModel):
    first_name: str = ""
    required_field_ids: list[str] = Field(default_factory=list)

    @field_validator("first_name", mode="before")
    @classmethod
    def _first_name_strip(cls, v: object) -> str:
        if v is None:
            return ""
        return v.strip() if isinstance(v, str) else str(v).strip()


class CreateInvitationInput(BaseModel):
    event_id: str
    inviter_id: str
    name: str
    ticket_id: str | None = None
    destination: str
    destination_type: InvitationDestinationType
    expires_at: str
    metadata: dict = {}
    tag_ids: list[str] = []
    guest_slot_count: int = 0
    guests: list[CreateInvitationGuestSlotInput] = Field(default_factory=list)

    @field_validator("guest_slot_count", mode="before")
    @classmethod
    def _guest_slot_count_int(cls, v: object) -> int:
        if v is None:
            return 0
        if isinstance(v, bool):
            raise ValueError("guest_slot_count must be an integer")
        return int(v)

    @field_validator("name", mode="before")
    @classmethod
    def _require_name(cls, v: object) -> str:
        if v is None:
            raise ValueError("name is required")
        s = v.strip() if isinstance(v, str) else str(v).strip()
        if not s:
            raise ValueError("name must not be empty")
        return s

    @field_validator("ticket_id", mode="before")
    @classmethod
    def _blank_optional_ids(cls, v: str | None) -> str | None:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else v


class UpdateInvitationInput(BaseModel):
    event_id: str | None = None
    inviter_id: str | None = None
    ticket_id: str | None = None
    name: str | None = None
    destination: str | None = None
    destination_type: InvitationDestinationType | None = None
    expires_at: str | None = None
    metadata: dict | None = None
    tag_ids: list[str] | None = None
    guest_slot_count: int | None = None
    guests: list[CreateInvitationGuestSlotInput] | None = None

    @field_validator("guest_slot_count", mode="before")
    @classmethod
    def _guest_slot_count_optional_int(cls, v: object) -> int | None:
        if v is None:
            return None
        if isinstance(v, bool):
            raise ValueError("guest_slot_count must be an integer")
        return int(v)

    @field_validator("name", mode="before")
    @classmethod
    def _optional_name_nonempty(cls, v: object) -> str | None:
        if v is None:
            return None
        s = v.strip() if isinstance(v, str) else str(v).strip()
        if not s:
            raise ValueError("name must not be empty")
        return s

    @field_validator("ticket_id", mode="before")
    @classmethod
    def _blank_optional_ids(cls, v: str | None) -> str | None:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else v
