from typing import Any

from domain.attendees.entity import Attendee, AttendeeQueryParams
from domain.attendees.repository import AttendeeRepository
from infrastructure.config import EVENTS_COLLECTION_NAME, ATTENDEES_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestoreAttendeeRepository(AttendeeRepository):
    def __init__(self, db: Any) -> None:
        self._db = db

    def _coll(self, event_id: str):
        return self._db.collection(EVENTS_COLLECTION_NAME).document(event_id).collection(ATTENDEES_COLLECTION_NAME)

    def _dump(self, attendee: Attendee) -> dict[str, Any]:
        return attendee.model_dump(mode="json")

    def create(self, attendee: Attendee, event_id: str) -> Attendee:
        self._coll(event_id).document(attendee.id).set(self._dump(attendee))
        return attendee

    def get_by_id(self, id: str, event_id: str) -> Attendee | None:
        doc = self._coll(event_id).document(id).get()
        if not doc.exists:
            return None
        return Attendee.model_validate(doc.to_dict())

    def list(self, event_id: str, query_params: AttendeeQueryParams) -> list[Attendee]:
        query = self._coll(event_id)
        query = apply_filters(query, query_params, AttendeeQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Attendee.model_validate(d.to_dict()) for d in snapshot]

    def update_status(self, id: str, event_id: str, status: str, check_in_time: str | None) -> Attendee | None:
        ref = self._coll(event_id).document(id)
        if not ref.get().exists:
            return None
        updates = {"status": status, "updated_at": get_timestamp()}
        if check_in_time is not None:
            updates["check_in_time"] = check_in_time
        ref.update(updates)
        return self.get_by_id(id, event_id)
