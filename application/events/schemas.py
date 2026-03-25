from pydantic import BaseModel


class CreateEventInput(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    location_address: str | None = None
    location_link: str | None = None
    active: bool | None = None
    is_paid: bool | None = None
    is_online: bool | None = None
    tag_ids: list[str]
    imageURL: str | None = None


class UpdateEventInput(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    location_address: str | None = None
    location_link: str | None = None
    active: bool | None = None
    is_paid: bool | None = None
    is_online: bool | None = None
    tag_ids: list[str] | None = None
    imageURL: str | None = None
