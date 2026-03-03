from typing import Any

from backend_api.domain.events.entity import Event, EventQueryParams
from backend_api.domain.events.repository import EventRepository
from backend_api.infrastructure.config import EVENTS_COLLECTION_NAME
from backend_api.infrastructure.persistence.firestore_common import (
    apply_filters,
    get_timestamp,
)


class FirestoreEventRepository(EventRepository):
    def __init__(self, db: Any, collection_name: str = EVENTS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, event: Event) -> dict[str, Any]:
        return event.model_dump(mode="json")

    def create(self, event: Event) -> Event:
        self._coll.document(event.id).set(self._dump(event))
        return event

    def get_by_id(self, id: str) -> Event | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Event.model_validate(doc.to_dict())

    def list(self, query_params: EventQueryParams) -> list[Event]:
        query = self._coll
        query = apply_filters(query, query_params, EventQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Event.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, event: Event) -> Event:
        ref = self._coll.document(id)
        ref.update(self._dump(event))
        return event

    def soft_delete(self, id: str, last_updated_by: str) -> Event | None:
        ref = self._coll.document(id)
        doc = ref.get()
        if not doc.exists:
            return None
        ref.update({
            "deleted": True,
            "updated_at": get_timestamp(),
            "last_updated_by": last_updated_by,
        })
        return self.get_by_id(id)
