from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator


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
    status: Literal["active", "cancelled", "completed"]
    notes: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_ymd(cls, v: str) -> str:
        date.fromisoformat(v)
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_hm(cls, v: str) -> str:
        datetime.strptime(v, "%H:%M")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_tz(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except Exception:
            raise ValueError("Invalid timezone") from None
        return v


class UpdateScheduleInput(BaseModel):
    event_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    timezone: str | None = None
    exclusions: list[ScheduleExclusionInput] | None = None
    status: Literal["active", "cancelled", "completed"] | None = None
    notes: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_ymd_opt(cls, v: str | None) -> str | None:
        if v is None:
            return v
        date.fromisoformat(v)
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_hm_opt(cls, v: str | None) -> str | None:
        if v is None:
            return v
        datetime.strptime(v, "%H:%M")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_tz_opt(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            ZoneInfo(v)
        except Exception:
            raise ValueError("Invalid timezone") from None
        return v
