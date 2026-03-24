from domain.event_types.entity import EventType
from domain.event_types.exceptions import EventTypeNotFoundError
from domain.event_types.repository import EventTypeRepository
from application.event_types.schemas import UpdateEventTypeInput


def update_event_type(
    repo: EventTypeRepository,
    event_type_id: str,
    data: UpdateEventTypeInput,
    last_updated_by: str,
    updated_at: str,
) -> EventType:
    existing = repo.get_by_id(event_type_id)
    if existing is None:
        raise EventTypeNotFoundError(event_type_id)
    updates = data.model_dump(exclude_unset=True)
    updated_event_type = existing.model_copy(
        update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by},
    )
    return repo.update(event_type_id, updated_event_type)
