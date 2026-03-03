from backend_api.domain.events.entity import Event
from backend_api.domain.events.exceptions import EventNotFoundError
from backend_api.domain.events.repository import EventRepository


def delete_event(
    repo: EventRepository,
    event_id: str,
    last_updated_by: str,
) -> Event:
    result = repo.soft_delete(event_id, last_updated_by)
    if result is None:
        raise EventNotFoundError(event_id)
    return result
