from domain.locations.entity import LocationQueryParams
from domain.locations.repository import LocationRepository


def list_locations(repo: LocationRepository, query_params: LocationQueryParams):
    return repo.list(query_params)
