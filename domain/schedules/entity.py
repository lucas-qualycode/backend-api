from typing import ClassVar

from pydantic import BaseModel


class ScheduleExclusion(BaseModel):
    id: str
    type: str
    value: str | list[str]
    description: str | None = None


class Schedule(BaseModel):
    id: str
    event_id: str
    parent_id: str | None = None
    stand_id: str | None = None
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    timezone: str
    exclusions: list[ScheduleExclusion]
    status: str
    notes: str | None = None
    created_at: str
    updated_at: str
    last_updated_by: str


class ScheduleQueryParams(BaseModel):
    event_id: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("event_id", "event_id", "=="),
        ("status", "status", "=="),
    ]
