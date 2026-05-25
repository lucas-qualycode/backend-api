from application.schedules.list_schedules import list_schedules
from domain.schedules.entity import ScheduleQueryParams
from domain.schedules.repository import ScheduleRepository


def embed_schedules_on_event_dicts(
    rows: list[dict],
    schedule_repo: ScheduleRepository,
) -> list[dict]:
    if not rows:
        return []
    for row in rows:
        event_id = row.get("id")
        if not event_id:
            row["schedules"] = []
            continue
        schedules = list_schedules(schedule_repo, ScheduleQueryParams(event_id=event_id))
        row["schedules"] = [s.model_dump(mode="json") for s in schedules]
    return rows
