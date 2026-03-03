from backend_api.domain.event_types.entity import EventType, EventTypeQueryParams
from backend_api.domain.event_types.repository import EventTypeRepository


def list_event_types(repo: EventTypeRepository, query_params: EventTypeQueryParams) -> list[EventType]:
    return repo.list(query_params)
