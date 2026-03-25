from pydantic import BaseModel


class CreateTagInput(BaseModel):
    name: str
    description: str | None = None
    active: bool = True
    parent_tag_id: str | None = None
    applies_to: list[str]


class UpdateTagInput(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None
    parent_tag_id: str | None = None
    applies_to: list[str] | None = None
