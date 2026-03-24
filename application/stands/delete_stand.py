from domain.stands.entity import Stand
from domain.stands.exceptions import StandNotFoundError
from domain.stands.repository import StandRepository


def delete_stand(repo: StandRepository, stand_id: str, event_id: str, last_updated_by: str) -> Stand:
    result = repo.soft_delete(stand_id, event_id, last_updated_by)
    if result is None:
        raise StandNotFoundError(stand_id)
    return result
