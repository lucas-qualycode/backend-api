from domain.addresses.entity import Address
from domain.addresses.exceptions import AddressNotFoundError
from domain.addresses.repository import AddressRepository


def get_address(repo: AddressRepository, address_id: str) -> Address:
    address = repo.get_by_id(address_id)
    if address is None:
        raise AddressNotFoundError(address_id)
    return address
