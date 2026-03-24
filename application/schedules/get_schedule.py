from domain.schedules.entity import Schedule
from domain.schedules.exceptions import ScheduleNotFoundError
from domain.schedules.repository import ScheduleRepository


def get_schedule(repo: ScheduleRepository, schedule_id: str) -> Schedule:
    schedule = repo.get_by_id(schedule_id)
    if schedule is None:
        raise ScheduleNotFoundError(schedule_id)
    return schedule
