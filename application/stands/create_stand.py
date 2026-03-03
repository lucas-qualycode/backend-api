import uuid
from backend_api.application.stands.schemas import CreateStandInput
from backend_api.domain.stands.entity import Stand, StandLocation, StandLocationCoordinates, StandTypeRef
from backend_api.domain.stands.repository import StandRepository

def create_stand(repo, data: CreateStandInput, event_id: str, last_updated_by: str, now: str):
    stand = Stand(
        id=str(uuid.uuid4()),
        event_id=event_id,
        name=data.name,
        location=StandLocation(zone=data.location.zone, coordinates=StandLocationCoordinates(x=data.location.coordinates.x, y=data.location.coordinates.y)),
        status=data.status,
        base_price=data.base_price,
        features=data.features,
        amenities=data.amenities,
        types=[StandTypeRef(id=t.id, name=t.name) for t in data.types],
        deleted=False,
        created_at=now,
        updated_at=now,
        last_updated_by=last_updated_by,
    )
    return repo.create(stand, event_id)
