import pytest

from application.field_definitions.schemas import CreateFieldDefinitionInput
from application.field_definitions.validation import validate_field_definition_create
from utils.errors import ValidationError


def test_validate_field_definition_accepts_text_with_lengths() -> None:
    validate_field_definition_create(
        CreateFieldDefinitionInput(
            key="full_name",
            label="Full name",
            field_type="text",
            min_length=1,
            max_length=100,
        )
    )


def test_validate_field_definition_rejects_unknown_type() -> None:
    with pytest.raises(ValidationError, match="field_type must be"):
        validate_field_definition_create(
            CreateFieldDefinitionInput(
                key="k",
                label="l",
                field_type="date",
            )
        )


def test_validate_field_definition_rejects_select_without_options() -> None:
    with pytest.raises(ValidationError, match="options must be a non-empty"):
        validate_field_definition_create(
            CreateFieldDefinitionInput(
                key="size",
                label="Size",
                field_type="select",
                options=[],
            )
        )


def test_validate_field_definition_rejects_text_with_numeric_rules() -> None:
    with pytest.raises(ValidationError, match="minimum/maximum are not allowed"):
        validate_field_definition_create(
            CreateFieldDefinitionInput(
                key="note",
                label="Note",
                field_type="text",
                minimum=1,
            )
        )
