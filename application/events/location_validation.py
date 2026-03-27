from domain.locations.repository import LocationRepository
from utils.errors import ValidationError


def resolve_location_id_for_event(
    location_repo: LocationRepository,
    location_id: str | None,
    is_online: bool,
    user_id: str,
) -> str | None:
    if is_online:
        return None
    if not location_id:
        raise ValidationError("location_id is required for in-person events")
    loc = location_repo.get_by_id(location_id)
    if loc is None or loc.deleted:
        raise ValidationError("Invalid location")
    if loc.created_by != user_id:
        raise ValidationError("Not allowed to use this location")
    return location_id
