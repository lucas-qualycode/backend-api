from domain.addresses.entity import Address, AddressQueryParams
from domain.addresses.repository import AddressRepository


def list_addresses(
    repo: AddressRepository,
    query_params: AddressQueryParams,
) -> list[Address]:
    return repo.list(query_params)
