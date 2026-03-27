from typing import Any

from domain.locations.entity import Location, LocationQueryParams
from domain.locations.repository import LocationRepository
from infrastructure.config import LOCATIONS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestoreLocationRepository(LocationRepository):
    def __init__(self, db: Any, collection_name: str = LOCATIONS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def create(self, location: Location) -> Location:
        self._coll.document(location.id).set(location.model_dump(mode="json"))
        return location

    def get_by_id(self, id: str) -> Location | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Location.model_validate(doc.to_dict())

    def get_by_ids(self, ids: list[str]) -> dict[str, Location]:
        if not ids:
            return {}
        unique = list(dict.fromkeys(ids))
        refs = [self._coll.document(i) for i in unique]
        docs = self._db.get_all(refs)
        out: dict[str, Location] = {}
        for d in docs:
            if d.exists:
                loc = Location.model_validate(d.to_dict())
                out[loc.id] = loc
        return out

    def list(self, query_params: LocationQueryParams) -> list[Location]:
        query = self._coll
        query = apply_filters(query, query_params, LocationQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        return [Location.model_validate(d.to_dict()) for d in query.get()]

    def update(self, id: str, location: Location) -> Location:
        self._coll.document(id).set(location.model_dump(mode="json"))
        return location

    def soft_delete(self, id: str, last_updated_by: str) -> Location | None:
        ref = self._coll.document(id)
        if not ref.get().exists:
            return None
        ref.update(
            {
                "deleted": True,
                "updated_at": get_timestamp(),
                "last_updated_by": last_updated_by,
            }
        )
        return self.get_by_id(id)
