from backend_api.domain.schedules.entity import Schedule
from backend_api.domain.schedules.exceptions import ScheduleNotFoundError
from backend_api.domain.schedules.repository import ScheduleRepository


def get_schedule(repo: ScheduleRepository, schedule_id: str) -> Schedule:
    schedule = repo.get_by_id(schedule_id)
    if schedule is None:
        raise ScheduleNotFoundError(schedule_id)
    return schedule
