from backend_api.domain.event_types.entity import EventType
from backend_api.domain.event_types.exceptions import EventTypeNotFoundError
from backend_api.domain.event_types.repository import EventTypeRepository


def delete_event_type(
    repo: EventTypeRepository,
    event_type_id: str,
    last_updated_by: str,
) -> EventType:
    result = repo.soft_delete(event_type_id, last_updated_by)
    if result is None:
        raise EventTypeNotFoundError(event_type_id)
    return result
