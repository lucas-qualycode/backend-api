from backend_api.domain.events.entity import Event
from backend_api.domain.events.exceptions import EventNotFoundError
from backend_api.domain.events.repository import EventRepository


def get_event(repo: EventRepository, event_id: str) -> Event:
    event = repo.get_by_id(event_id)
    if event is None:
        raise EventNotFoundError(event_id)
    return event
