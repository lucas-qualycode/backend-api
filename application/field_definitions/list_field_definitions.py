from domain.field_definitions.entity import FieldDefinition, FieldDefinitionQueryParams
from domain.field_definitions.repository import FieldDefinitionRepository


def list_field_definitions(
    repo: FieldDefinitionRepository,
    query_params: FieldDefinitionQueryParams,
) -> list[FieldDefinition]:
    return repo.list(query_params)
