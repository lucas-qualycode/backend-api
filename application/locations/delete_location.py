from domain.locations.entity import Location
from domain.locations.exceptions import LocationNotFoundError
from domain.locations.repository import LocationRepository
from utils.errors import ValidationError


def delete_location(
    repo: LocationRepository,
    location_id: str,
    user_id: str,
) -> Location:
    existing = repo.get_by_id(location_id)
    if existing is None or existing.deleted:
        raise LocationNotFoundError(location_id)
    if existing.created_by != user_id:
        raise ValidationError("Not allowed to delete this location")
    out = repo.soft_delete(location_id, user_id)
    if out is None:
        raise LocationNotFoundError(location_id)
    return out
