from application.field_definitions.schemas import UpdateFieldDefinitionInput
from application.field_definitions.validation import (
    validate_field_definition_state,
    validate_field_definition_update,
)
from domain.field_definitions.entity import FieldDefinition
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError
from domain.field_definitions.repository import FieldDefinitionRepository


def update_field_definition(
    repo: FieldDefinitionRepository,
    field_id: str,
    data: UpdateFieldDefinitionInput,
    last_updated_by: str,
    now: str,
) -> FieldDefinition:
    existing = repo.get_by_id(field_id)
    if existing is None or existing.deleted:
        raise FieldDefinitionNotFoundError(field_id)
    validate_field_definition_update(data)
    patch = data.model_dump(exclude_unset=True)
    if "key" in patch and patch["key"] is not None:
        patch["key"] = patch["key"].strip()
    if "label" in patch and patch["label"] is not None:
        patch["label"] = patch["label"].strip()
    if "description" in patch:
        raw = patch["description"]
        patch["description"] = raw.strip() if raw and str(raw).strip() else None
    if "options" in patch and patch["options"] is not None:
        patch["options"] = [x.strip() for x in patch["options"]]
    row = existing.model_copy(update={**patch, "updated_at": now, "last_updated_by": last_updated_by})
    validate_field_definition_state(row)
    return repo.update(field_id, row)
