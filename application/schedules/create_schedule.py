import uuid

from backend_api.application.schedules.schemas import CreateScheduleInput
from backend_api.domain.schedules.entity import Schedule, ScheduleExclusion
from backend_api.domain.schedules.repository import ScheduleRepository


def create_schedule(
    repo: ScheduleRepository,
    data: CreateScheduleInput,
    last_updated_by: str,
    now: str,
) -> Schedule:
    exclusions = [
        ScheduleExclusion(
            id=str(uuid.uuid4()),
            type=e.type,
            value=e.value,
            description=e.description,
        )
        for e in data.exclusions
    ]
    schedule = Schedule(
        id=str(uuid.uuid4()),
        event_id=data.event_id,
        parent_id=None,
        stand_id=None,
        start_date=data.start_date,
        end_date=data.end_date,
        start_time=data.start_time,
        end_time=data.end_time,
        timezone=data.timezone,
        exclusions=exclusions,
        status=data.status,
        notes=data.notes,
        created_at=now,
        updated_at=now,
        last_updated_by=last_updated_by,
    )
    return repo.create(schedule)
