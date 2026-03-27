from application.schedules.event_access import ensure_user_owns_event
from domain.events.repository import EventRepository
from domain.schedules.exceptions import ScheduleNotFoundError
from domain.schedules.repository import ScheduleRepository


def delete_schedule(
    repo: ScheduleRepository,
    event_repo: EventRepository,
    schedule_id: str,
    user_id: str,
) -> None:
    existing = repo.get_by_id(schedule_id)
    if existing is None:
        raise ScheduleNotFoundError(schedule_id)
    ensure_user_owns_event(event_repo, existing.event_id, user_id)
    repo.delete(schedule_id)
