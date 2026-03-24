from domain.event_types.entity import EventType, EventTypeQueryParams
from domain.event_types.repository import EventTypeRepository


def list_event_types(repo: EventTypeRepository, query_params: EventTypeQueryParams) -> list[EventType]:
    return repo.list(query_params)
