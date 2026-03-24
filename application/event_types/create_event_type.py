import uuid

from domain.event_types.entity import EventType
from domain.event_types.repository import EventTypeRepository
from application.event_types.schemas import CreateEventTypeInput


def create_event_type(
    repo: EventTypeRepository,
    data: CreateEventTypeInput,
    created_by: str,
    now: str,
) -> EventType:
    event_type = EventType(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        active=data.active,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
    )
    return repo.create(event_type)
