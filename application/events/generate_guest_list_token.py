import secrets

from domain.events.entity import Event
from domain.events.exceptions import EventNotFoundError
from domain.events.repository import EventRepository


def generate_guest_list_token(
    repo: EventRepository,
    event_id: str,
    last_updated_by: str,
    updated_at: str,
) -> str:
    event = repo.get_by_id(event_id)
    if event is None:
        raise EventNotFoundError(event_id)
    if event.deleted:
        raise EventNotFoundError(event_id)
    token = secrets.token_hex(32)
    updated = event.model_copy(
        update={
            "guest_list_token": token,
            "updated_at": updated_at,
            "last_updated_by": last_updated_by,
        },
    )
    repo.update(event_id, updated)
    return token
