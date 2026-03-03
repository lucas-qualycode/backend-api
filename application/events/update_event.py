from backend_api.application.events.schemas import UpdateEventInput
from backend_api.domain.events.entity import Event
from backend_api.domain.events.exceptions import EventNotFoundError
from backend_api.domain.events.repository import EventRepository
from backend_api.utils.validators import validate_name, validate_url


def update_event(
    repo: EventRepository,
    event_id: str,
    data: UpdateEventInput,
    last_updated_by: str,
    updated_at: str,
) -> Event:
    existing = repo.get_by_id(event_id)
    if existing is None:
        raise EventNotFoundError(event_id)
    if existing.deleted:
        raise EventNotFoundError(event_id)
    if data.name is not None:
        validate_name(data.name)
    validate_url(data.imageURL, "imageURL")
    validate_url(data.location_link, "location_link")
    updates = data.model_dump(exclude_unset=True)
    updated_event = existing.model_copy(
        update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by},
    )
    return repo.update(event_id, updated_event)
