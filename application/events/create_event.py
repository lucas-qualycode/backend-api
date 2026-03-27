import uuid

from application.events.location_validation import resolve_location_id_for_event
from application.events.schemas import CreateEventInput
from domain.events.entity import Event
from domain.events.repository import EventRepository
from domain.locations.repository import LocationRepository
from utils.validators import validate_name, validate_url


def create_event(
    repo: EventRepository,
    location_repo: LocationRepository,
    data: CreateEventInput,
    created_by: str,
    now: str,
) -> Event:
    validate_name(data.name)
    validate_url(data.imageURL, "imageURL")
    is_online = data.is_online if data.is_online is not None else False
    location_id = resolve_location_id_for_event(
        location_repo,
        data.location_id,
        is_online,
        created_by,
    )
    event = Event(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        location_id=location_id,
        active=data.active if data.active is not None else True,
        is_paid=data.is_paid if data.is_paid is not None else False,
        is_online=is_online,
        imageURL=data.imageURL,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
    )
    return repo.create(event)
