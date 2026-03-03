from pydantic import BaseModel


class StandLocationCoordinates(BaseModel):
    x: float
    y: float


class StandLocationInput(BaseModel):
    zone: str
    coordinates: StandLocationCoordinates


class StandTypeRefInput(BaseModel):
    id: str
    name: str


class CreateStandInput(BaseModel):
    name: str
    location: StandLocationInput
    types: list[StandTypeRefInput]
    status: str = "available"
    base_price: int = 0
    features: list[str] = []
    amenities: list[str] = []


class UpdateStandInput(BaseModel):
    name: str | None = None
    location: StandLocationInput | None = None
    status: str | None = None
    base_price: int | None = None
    features: list[str] | None = None
    amenities: list[str] | None = None
