from application.field_definitions.schemas import (
    CreateFieldDefinitionInput,
    UpdateFieldDefinitionInput,
)
from domain.field_definitions.entity import FieldDefinition, FieldType
from utils.errors import ValidationError


def validate_field_definition_create(data: CreateFieldDefinitionInput) -> None:
    if not data.key or not data.key.strip():
        raise ValidationError("key is required")
    if not data.label or not data.label.strip():
        raise ValidationError("label is required")
    _validate_type_and_rules(
        field_type=data.field_type,
        min_length=data.min_length,
        max_length=data.max_length,
        minimum=data.minimum,
        maximum=data.maximum,
        options=data.options,
    )


def validate_field_definition_update(data: UpdateFieldDefinitionInput) -> None:
    if data.key is not None and not data.key.strip():
        raise ValidationError("key cannot be empty")
    if data.label is not None and not data.label.strip():
        raise ValidationError("label cannot be empty")
    if (
        data.field_type is not None
        or data.min_length is not None
        or data.max_length is not None
        or data.minimum is not None
        or data.maximum is not None
        or data.options is not None
    ):
        _validate_type_and_rules(
            field_type=data.field_type,
            min_length=data.min_length,
            max_length=data.max_length,
            minimum=data.minimum,
            maximum=data.maximum,
            options=data.options,
        )


def validate_field_definition_state(row: FieldDefinition) -> None:
    _validate_type_and_rules(
        field_type=row.field_type,
        min_length=row.min_length,
        max_length=row.max_length,
        minimum=row.minimum,
        maximum=row.maximum,
        options=row.options,
    )


def _validate_type_and_rules(
    *,
    field_type: str | None,
    min_length: int | None,
    max_length: int | None,
    minimum: float | None,
    maximum: float | None,
    options: list[str] | None,
) -> None:
    if field_type not in (
        FieldType.TEXT,
        FieldType.NUMBER,
        FieldType.BOOLEAN,
        FieldType.SELECT,
    ):
        raise ValidationError("field_type must be text, number, boolean, or select")
    if min_length is not None and min_length < 0:
        raise ValidationError("min_length must be >= 0")
    if max_length is not None and max_length < 0:
        raise ValidationError("max_length must be >= 0")
    if min_length is not None and max_length is not None and min_length > max_length:
        raise ValidationError("min_length cannot be greater than max_length")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValidationError("minimum cannot be greater than maximum")
    if field_type == FieldType.SELECT:
        if not options or not all(isinstance(x, str) and x.strip() for x in options):
            raise ValidationError("options must be a non-empty string array for select")
    elif options:
        raise ValidationError("options are only allowed for select field_type")
    if field_type == FieldType.TEXT:
        if minimum is not None or maximum is not None:
            raise ValidationError("minimum/maximum are not allowed for text field_type")
    elif field_type == FieldType.NUMBER:
        if min_length is not None or max_length is not None:
            raise ValidationError("min_length/max_length are not allowed for number field_type")
    elif field_type == FieldType.BOOLEAN:
        if any(x is not None for x in (min_length, max_length, minimum, maximum)):
            raise ValidationError("boolean field_type cannot have min/max/length rules")
