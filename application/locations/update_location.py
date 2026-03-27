from application.locations.schemas import UpdateLocationInput
from domain.locations.entity import Location
from domain.locations.exceptions import LocationNotFoundError
from domain.locations.repository import LocationRepository
from utils.errors import ValidationError
from utils.validators import (
    validate_country_code,
    validate_latitude,
    validate_longitude,
    validate_url,
)


def update_location(
    repo: LocationRepository,
    location_id: str,
    data: UpdateLocationInput,
    user_id: str,
    now: str,
) -> Location:
    existing = repo.get_by_id(location_id)
    if existing is None or existing.deleted:
        raise LocationNotFoundError(location_id)
    if existing.created_by != user_id:
        raise ValidationError("Not allowed to update this location")
    validate_url(data.maps_url, "maps_url")
    validate_url(data.website_url, "website_url")
    validate_latitude(data.latitude)
    validate_longitude(data.longitude)
    if data.country is not None:
        validate_country_code(data.country.upper())
    updates = data.model_dump(exclude_unset=True)
    if "venue_name" in updates and updates["venue_name"] is not None:
        vn = updates["venue_name"].strip()
        if not vn:
            raise ValidationError("venue_name is required")
        updates["venue_name"] = vn
    if "country" in updates and updates["country"] is not None:
        updates["country"] = updates["country"].upper()
    merged = existing.model_copy(update={**updates, "updated_at": now, "last_updated_by": user_id})
    return repo.update(location_id, merged)
