from pydantic import BaseModel


class CreateAddressInput(BaseModel):
    userId: str
    type: str
    isDefault: bool = False
    street: str
    city: str
    state: str
    postalCode: str
    country: str
    apartment: str | None = None
    label: str | None = None


class UpdateAddressInput(BaseModel):
    userId: str | None = None
    type: str | None = None
    isDefault: bool | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postalCode: str | None = None
    country: str | None = None
    apartment: str | None = None
    label: str | None = None
