from typing import ClassVar

from pydantic import BaseModel


class Address(BaseModel):
    id: str
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
    createdAt: str
    updatedAt: str


class AddressQueryParams(BaseModel):
    user_id: str | None = None
    type: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("user_id", "userId", "=="),
        ("type", "type", "=="),
    ]
