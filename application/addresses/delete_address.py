from backend_api.domain.addresses.exceptions import AddressNotFoundError
from backend_api.domain.addresses.repository import AddressRepository


def delete_address(repo: AddressRepository, address_id: str) -> None:
    existing = repo.get_by_id(address_id)
    if existing is None:
        raise AddressNotFoundError(address_id)
    repo.delete(address_id)
