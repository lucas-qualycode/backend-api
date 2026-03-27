from domain.events.repository import EventRepository

from application.events.get_event import get_event
from utils.errors import ValidationError


def ensure_user_owns_event(event_repo: EventRepository, event_id: str, uid: str) -> None:
    event = get_event(event_repo, event_id)
    if event.created_by != uid:
        raise ValidationError("Not allowed to manage schedules for this event")
