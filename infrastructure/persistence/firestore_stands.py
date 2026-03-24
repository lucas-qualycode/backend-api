from typing import Any

from domain.stands.entity import Stand, StandQueryParams
from domain.stands.repository import StandRepository
from infrastructure.config import EVENTS_COLLECTION_NAME, STANDS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import (
    apply_filters,
    get_timestamp,
)


class FirestoreStandRepository(StandRepository):
    def __init__(self, db: Any) -> None:
        self._db = db

    def _coll(self, event_id: str):
        return self._db.collection(EVENTS_COLLECTION_NAME).document(event_id).collection(STANDS_COLLECTION_NAME)

    def _dump(self, stand: Stand) -> dict[str, Any]:
        return stand.model_dump(mode="json")

    def create(self, stand: Stand, event_id: str) -> Stand:
        self._coll(event_id).document(stand.id).set(self._dump(stand))
        return stand

    def get_by_id(self, id: str, event_id: str) -> Stand | None:
        doc = self._coll(event_id).document(id).get()
        if not doc.exists:
            return None
        return Stand.model_validate(doc.to_dict())

    def list(self, event_id: str, query_params: StandQueryParams) -> list[Stand]:
        query = self._coll(event_id)
        query = apply_filters(query, query_params, StandQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Stand.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, event_id: str, stand: Stand) -> Stand:
        self._coll(event_id).document(id).update(self._dump(stand))
        return stand

    def soft_delete(self, id: str, event_id: str, last_updated_by: str) -> Stand | None:
        ref = self._coll(event_id).document(id)
        doc = ref.get()
        if not doc.exists:
            return None
        ref.update({
            "deleted": True,
            "updated_at": get_timestamp(),
            "last_updated_by": last_updated_by,
        })
        return self.get_by_id(id, event_id)
