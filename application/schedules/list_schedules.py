from backend_api.domain.schedules.entity import Schedule, ScheduleQueryParams
from backend_api.domain.schedules.repository import ScheduleRepository


def list_schedules(repo: ScheduleRepository, query_params: ScheduleQueryParams) -> list[Schedule]:
    return repo.list(query_params)
