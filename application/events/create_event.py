import uuid

from backend_api.application.events.schemas import CreateEventInput
from backend_api.domain.events.entity import Event
from backend_api.domain.events.repository import EventRepository
from backend_api.utils.validators import validate_name, validate_url


def create_event(
    repo: EventRepository,
    data: CreateEventInput,
    created_by: str,
    now: str,
) -> Event:
    validate_name(data.name)
    validate_url(data.imageURL, "imageURL")
    validate_url(data.location_link, "location_link")
    event = Event(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        location=data.location,
        location_address=data.location_address,
        location_link=data.location_link,
        active=data.active if data.active is not None else True,
        is_paid=data.is_paid if data.is_paid is not None else False,
        is_online=data.is_online if data.is_online is not None else False,
        type_ids=data.type_ids,
        imageURL=data.imageURL,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
    )
    return repo.create(event)
