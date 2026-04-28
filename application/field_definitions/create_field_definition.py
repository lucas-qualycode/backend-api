import uuid

from application.field_definitions.schemas import CreateFieldDefinitionInput
from application.field_definitions.validation import validate_field_definition_create
from domain.field_definitions.entity import FieldDefinition
from domain.field_definitions.repository import FieldDefinitionRepository


def create_field_definition(
    repo: FieldDefinitionRepository,
    data: CreateFieldDefinitionInput,
    created_by: str,
    now: str,
) -> FieldDefinition:
    validate_field_definition_create(data)
    row = FieldDefinition(
        id=str(uuid.uuid4()),
        key=data.key.strip(),
        label=data.label.strip(),
        description=data.description.strip() if data.description and data.description.strip() else None,
        field_type=data.field_type,
        required_default=data.required_default,
        format=data.format,
        min_length=data.min_length,
        max_length=data.max_length,
        minimum=data.minimum,
        maximum=data.maximum,
        options=[x.strip() for x in data.options],
        active=data.active,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
    )
    return repo.create(row)
