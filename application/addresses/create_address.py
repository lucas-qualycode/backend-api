import uuid

from application.addresses.schemas import CreateAddressInput
from domain.addresses.entity import Address
from domain.addresses.repository import AddressRepository


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
