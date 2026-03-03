from pydantic import BaseModel


class CreateInvitationInput(BaseModel):
    event_id: str
    inviter_id: str
    ticket_ids: list[str] = []
    type: str
    destination: str
    destination_type: str
    expires_at: str
    metadata: dict = {}


class UpdateInvitationInput(BaseModel):
    event_id: str | None = None
    inviter_id: str | None = None
    ticket_ids: list[str] | None = None
    type: str | None = None
    destination: str | None = None
    destination_type: str | None = None
    expires_at: str | None = None
    metadata: dict | None = None
