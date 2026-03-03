from pydantic import BaseModel


class CreateAttendeeInput(BaseModel):
    event_id: str
    user_id: str
    user_product_id: str
    invitation_id: str | None = None
    metadata: dict = {}
