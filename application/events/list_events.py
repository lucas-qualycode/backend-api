from backend_api.domain.events.entity import Event, EventQueryParams
from backend_api.domain.events.repository import EventRepository


def list_events(repo: EventRepository, query_params: EventQueryParams) -> list[Event]:
    return repo.list(query_params)
