from typing import Any
from domain.event_types.entity import EventType, EventTypeQueryParams
from domain.event_types.repository import EventTypeRepository
from infrastructure.config import EVENT_TYPES_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp

class FirestoreEventTypeRepository(EventTypeRepository):
    def __init__(self, db: Any, collection_name: str = EVENT_TYPES_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)
    def _dump(self, entity: EventType): return entity.model_dump(mode="json")
    def create(self, event_type: EventType) -> EventType:
        self._coll.document(event_type.id).set(self._dump(event_type))
        return event_type
    def get_by_id(self, id: str): doc = self._coll.document(id).get(); return EventType.model_validate(doc.to_dict()) if doc.exists else None
    def list(self, q: EventTypeQueryParams):
        query = apply_filters(self._coll, q, EventTypeQueryParams.FILTER_SPEC)
        if q.limit: query = query.limit(q.limit)
        if q.offset: query = query.offset(q.offset)
        return [EventType.model_validate(d.to_dict()) for d in query.get()]
    def update(self, id: str, et: EventType): self._coll.document(id).update(self._dump(et)); return et
    def soft_delete(self, id: str, last_updated_by: str):
        ref = self._coll.document(id)
        if not ref.get().exists: return None
        ref.update({"deleted": True, "updated_at": get_timestamp(), "last_updated_by": last_updated_by})
        return self.get_by_id(id)
