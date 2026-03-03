from backend_api.application.stands.schemas import UpdateStandInput
from backend_api.domain.stands.entity import Stand
from backend_api.domain.stands.exceptions import StandNotFoundError
from backend_api.domain.stands.repository import StandRepository


def update_stand(
    repo: StandRepository,
    stand_id: str,
    event_id: str,
    data: UpdateStandInput,
    last_updated_by: str,
    updated_at: str,
) -> Stand:
    existing = repo.get_by_id(stand_id, event_id)
    if existing is None:
        raise StandNotFoundError(stand_id)
    updates = data.model_dump(exclude_unset=True)
    if "location" in updates and updates["location"] is not None:
        loc = updates["location"]
        updates["location"] = {"zone": loc["zone"], "coordinates": loc["coordinates"]}
    updated_stand = existing.model_copy(update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by})
    return repo.update(stand_id, event_id, updated_stand)
