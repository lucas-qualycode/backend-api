from backend_api.domain.stands.entity import Stand, StandQueryParams
from backend_api.domain.stands.repository import StandRepository

def list_stands(repo: StandRepository, event_id: str, query_params: StandQueryParams) -> list[Stand]:
    return repo.list(event_id, query_params)
