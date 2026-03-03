from pydantic import BaseModel


class CreateEventTypeInput(BaseModel):
    name: str
    description: str | None = None
    active: bool = True


class UpdateEventTypeInput(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None
