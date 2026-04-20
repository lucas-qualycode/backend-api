from domain.field_definitions.entity import FieldDefinition
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError
from domain.field_definitions.repository import FieldDefinitionRepository


def get_field_definition(repo: FieldDefinitionRepository, field_id: str) -> FieldDefinition:
    row = repo.get_by_id(field_id)
    if row is None or row.deleted:
        raise FieldDefinitionNotFoundError(field_id)
    return row
