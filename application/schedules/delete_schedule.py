from domain.schedules.exceptions import ScheduleNotFoundError
from domain.schedules.repository import ScheduleRepository


def delete_schedule(repo: ScheduleRepository, schedule_id: str) -> None:
    existing = repo.get_by_id(schedule_id)
    if existing is None:
        raise ScheduleNotFoundError(schedule_id)
    repo.delete(schedule_id)
