import uuid

from application.schedules.event_access import ensure_user_owns_event
from application.schedules.schemas import UpdateScheduleInput
from domain.events.repository import EventRepository
from domain.schedules.entity import Schedule, ScheduleExclusion
from domain.schedules.exceptions import ScheduleNotFoundError
from domain.schedules.repository import ScheduleRepository


def update_schedule(
    repo: ScheduleRepository,
    event_repo: EventRepository,
    schedule_id: str,
    data: UpdateScheduleInput,
    last_updated_by: str,
    updated_at: str,
) -> Schedule:
    existing = repo.get_by_id(schedule_id)
    if existing is None:
        raise ScheduleNotFoundError(schedule_id)
    ensure_user_owns_event(event_repo, existing.event_id, last_updated_by)
    updates = data.model_dump(exclude_unset=True)
    new_event_id = updates.get("event_id")
    if new_event_id is not None and new_event_id != existing.event_id:
        ensure_user_owns_event(event_repo, new_event_id, last_updated_by)
    if "exclusions" in updates and updates["exclusions"] is not None:
        updates["exclusions"] = [
            ScheduleExclusion(
                id=str(uuid.uuid4()),
                type=e["type"],
                value=e["value"],
                description=e.get("description"),
            )
            for e in updates["exclusions"]
        ]
    updated_schedule = existing.model_copy(
        update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by}
    )
    return repo.update(schedule_id, updated_schedule)
