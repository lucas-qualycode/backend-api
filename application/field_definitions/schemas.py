from pydantic import BaseModel, Field


class CreateFieldDefinitionInput(BaseModel):
    key: str
    label: str
    description: str | None = None
    field_type: str
    required_default: bool = False
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None
    options: list[str] = Field(default_factory=list)
    active: bool = True


class UpdateFieldDefinitionInput(BaseModel):
    key: str | None = None
    label: str | None = None
    description: str | None = None
    field_type: str | None = None
    required_default: bool | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None
    options: list[str] | None = None
    active: bool | None = None
