import uuid

from backend_api.application.addresses.schemas import CreateAddressInput
from backend_api.domain.addresses.entity import Address
from backend_api.domain.addresses.repository import AddressRepository


def create_address(
    repo: AddressRepository,
    data: CreateAddressInput,
    now: str,
) -> Address:
    address = Address(
        id=str(uuid.uuid4()),
        userId=data.userId,
        type=data.type,
        isDefault=data.isDefault,
        street=data.street,
        city=data.city,
        state=data.state,
        postalCode=data.postalCode,
        country=data.country,
        apartment=data.apartment,
        label=data.label,
        createdAt=now,
        updatedAt=now,
    )
    return repo.create(address)
