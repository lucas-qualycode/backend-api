from backend_api.domain.stands.entity import Stand
from backend_api.domain.stands.exceptions import StandNotFoundError
from backend_api.domain.stands.repository import StandRepository

def get_stand(repo: StandRepository, stand_id: str, event_id: str) -> Stand:
    stand = repo.get_by_id(stand_id, event_id)
    if stand is None:
        raise StandNotFoundError(stand_id)
    return stand
