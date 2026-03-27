from typing import ClassVar

from pydantic import BaseModel


class Location(BaseModel):
    id: str
    venue_name: str
    street_line1: str | None = None
    street_line2: str | None = None
    locality: str | None = None
    region: str | None = None
    postal_code: str | None = None
    country: str | None = None
    formatted_address: str | None = None
    maps_url: str | None = None
    website_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    place_provider: str | None = None
    place_id: str | None = None
    deleted: bool
    created_at: str
    updated_at: str
    created_by: str
    last_updated_by: str


class LocationQueryParams(BaseModel):
    created_by: str | None = None
    deleted: bool | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("created_by", "created_by", "=="),
        ("deleted", "deleted", "=="),
    ]
