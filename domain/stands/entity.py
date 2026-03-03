from typing import ClassVar, Any

from pydantic import BaseModel


class StandLocationCoordinates(BaseModel):
    x: float
    y: float


class StandLocation(BaseModel):
    zone: str
    coordinates: StandLocationCoordinates


class StandTypeRef(BaseModel):
    id: str
    name: str


class Stand(BaseModel):
    id: str
    event_id: str
    name: str
    location: StandLocation
    status: str
    base_price: int
    features: list[str]
    amenities: list[str]
    types: list[StandTypeRef]
    deleted: bool
    created_at: str
    updated_at: str
    last_updated_by: str


class StandQueryParams(BaseModel):
    name: str | None = None
    status: str | None = None
    zone: str | None = None
    deleted: bool | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("name", "name", "=="),
        ("status", "status", "=="),
        ("zone", "location.zone", "=="),
        ("deleted", "deleted", "=="),
    ]
