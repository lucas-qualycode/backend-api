from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class FieldType:
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class FieldDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    key: str
    label: str
    description: str | None = None
    field_type: str
    required_default: bool = False
    format: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None
    options: list[str] = Field(default_factory=list)
    active: bool = True
    deleted: bool = False
    created_at: str
    updated_at: str
    created_by: str
    last_updated_by: str


class FieldDefinitionQueryParams(BaseModel):
    active: bool | None = None
    deleted: bool | None = None
    field_type: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("active", "active", "=="),
        ("deleted", "deleted", "=="),
        ("field_type", "field_type", "=="),
    ]
