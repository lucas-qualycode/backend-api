from domain.event_types.entity import EventType
from domain.event_types.exceptions import EventTypeNotFoundError
from domain.event_types.repository import EventTypeRepository


def get_event_type(repo: EventTypeRepository, event_type_id: str) -> EventType:
    event_type = repo.get_by_id(event_type_id)
    if event_type is None:
        raise EventTypeNotFoundError(event_type_id)
    return event_type
