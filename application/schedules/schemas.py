from pydantic import BaseModel


class ScheduleExclusionInput(BaseModel):
    type: str
    value: str | list[str]
    description: str | None = None


class CreateScheduleInput(BaseModel):
    event_id: str
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    timezone: str
    exclusions: list[ScheduleExclusionInput] = []
    status: str
    notes: str | None = None


class UpdateScheduleInput(BaseModel):
    event_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    timezone: str | None = None
    exclusions: list[ScheduleExclusionInput] | None = None
    status: str | None = None
    notes: str | None = None
