from enum import Enum

from pydantic import BaseModel, Field


class FieldTypeInput(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class FieldFormatInput(str, Enum):
    CPF = "cpf"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    TIME_ISO = "time_iso"
    DATE_ISO = "date_iso"
    DATETIME_ISO = "datetime_iso"


class CreateFieldDefinitionInput(BaseModel):
    key: str
    label: str
    description: str | None = None
    field_type: FieldTypeInput
    required_default: bool = False
    format: FieldFormatInput | None = None
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
    field_type: FieldTypeInput | None = None
    required_default: bool | None = None
    format: FieldFormatInput | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None
    options: list[str] | None = None
    active: bool | None = None
