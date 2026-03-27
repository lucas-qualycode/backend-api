import uuid

from application.locations.schemas import CreateLocationInput
from domain.locations.entity import Location
from domain.locations.repository import LocationRepository
from utils.errors import ValidationError
from utils.validators import (
    validate_country_code,
    validate_latitude,
    validate_longitude,
    validate_url,
)


def create_location(
    repo: LocationRepository,
    data: CreateLocationInput,
    created_by: str,
    now: str,
) -> Location:
    name = data.venue_name.strip()
    if not name:
        raise ValidationError("venue_name is required")
    validate_url(data.maps_url, "maps_url")
    validate_url(data.website_url, "website_url")
    validate_latitude(data.latitude)
    validate_longitude(data.longitude)
    country: str | None = None
    if data.country is not None and data.country.strip():
        country = data.country.strip().upper()
        validate_country_code(country)
    location = Location(
        id=str(uuid.uuid4()),
        venue_name=name,
        street_line1=data.street_line1,
        street_line2=data.street_line2,
        locality=data.locality,
        region=data.region,
        postal_code=data.postal_code,
        country=country,
        formatted_address=data.formatted_address,
        maps_url=data.maps_url,
        website_url=data.website_url,
        latitude=data.latitude,
        longitude=data.longitude,
        place_provider=data.place_provider,
        place_id=data.place_id,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
    )
    return repo.create(location)
