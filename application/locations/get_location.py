from domain.locations.entity import Location
from domain.locations.exceptions import LocationNotFoundError
from domain.locations.repository import LocationRepository


def get_location(repo: LocationRepository, location_id: str) -> Location:
    loc = repo.get_by_id(location_id)
    if loc is None or loc.deleted:
        raise LocationNotFoundError(location_id)
    return loc
