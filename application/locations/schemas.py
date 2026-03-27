from pydantic import BaseModel, Field


class CreateLocationInput(BaseModel):
    venue_name: str = Field(min_length=1, max_length=256)
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


class UpdateLocationInput(BaseModel):
    venue_name: str | None = Field(default=None, min_length=1, max_length=256)
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
