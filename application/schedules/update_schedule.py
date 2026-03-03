import uuid

from backend_api.application.schedules.schemas import UpdateScheduleInput
from backend_api.domain.schedules.entity import Schedule, ScheduleExclusion
from backend_api.domain.schedules.exceptions import ScheduleNotFoundError
from backend_api.domain.schedules.repository import ScheduleRepository


def update_schedule(
    repo: ScheduleRepository,
    schedule_id: str,
    data: UpdateScheduleInput,
    last_updated_by: str,
    updated_at: str,
) -> Schedule:
    existing = repo.get_by_id(schedule_id)
    if existing is None:
        raise ScheduleNotFoundError(schedule_id)
    updates = data.model_dump(exclude_unset=True)
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
