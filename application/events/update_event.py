from application.events.location_validation import resolve_location_id_for_event
from application.events.schemas import UpdateEventInput
from domain.events.entity import Event
from domain.events.exceptions import EventNotFoundError
from domain.events.repository import EventRepository
from domain.locations.repository import LocationRepository
from utils.validators import validate_name, validate_url


def update_event(
    repo: EventRepository,
    location_repo: LocationRepository,
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
    updates = data.model_dump(exclude_unset=True)
    updates.pop("tag_ids", None)

    next_is_online = data.is_online if data.is_online is not None else existing.is_online

    if next_is_online:
        next_location_id = None
    else:
        unset_fields = data.model_dump(exclude_unset=True)
        if "location_id" in unset_fields:
            candidate = data.location_id
        else:
            candidate = existing.location_id
        next_location_id = resolve_location_id_for_event(
            location_repo,
            candidate,
            False,
            last_updated_by,
        )

    updates.pop("is_online", None)
    updates.pop("location_id", None)

    updated_event = existing.model_copy(
        update={
            **updates,
            "is_online": next_is_online,
            "location_id": next_location_id,
            "updated_at": updated_at,
            "last_updated_by": last_updated_by,
        },
    )
    return repo.update(event_id, updated_event)
