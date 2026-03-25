from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class AppliesTo:
    EVENT = "EVENT"
    PRODUCT = "PRODUCT"
    INVITATION = "INVITATION"


class Tag(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    parent_tag_id: str | None = None
    applies_to: list[str] = Field(default_factory=list)
    depth: int = 0
    active: bool
    deleted: bool
    created_at: str
    updated_at: str
    created_by: str
    last_updated_by: str


class TagQueryParams(BaseModel):
    name: str | None = None
    active: bool | None = None
    deleted: bool | None = None
    parent_tag_id: str | None = None
    applies_to: str | None = None
    roots_only: bool = False
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("active", "active", "=="),
        ("deleted", "deleted", "=="),
        ("parent_tag_id", "parent_tag_id", "=="),
        ("applies_to", "applies_to", "array_contains"),
    ]
