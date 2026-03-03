from backend_api.application.addresses.schemas import UpdateAddressInput
from backend_api.domain.addresses.entity import Address
from backend_api.domain.addresses.exceptions import AddressNotFoundError
from backend_api.domain.addresses.repository import AddressRepository


def update_address(
    repo: AddressRepository,
    address_id: str,
    data: UpdateAddressInput,
    updated_at: str,
) -> Address:
    existing = repo.get_by_id(address_id)
    if existing is None:
        raise AddressNotFoundError(address_id)
    updates = data.model_dump(exclude_unset=True)
    updated_address = existing.model_copy(update={**updates, "updatedAt": updated_at})
    return repo.update(address_id, updated_address)
