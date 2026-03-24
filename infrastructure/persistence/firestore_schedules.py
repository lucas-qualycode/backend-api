from typing import Any

from domain.schedules.entity import Schedule, ScheduleQueryParams
from domain.schedules.repository import ScheduleRepository
from infrastructure.config import SCHEDULES_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters


class FirestoreScheduleRepository(ScheduleRepository):
    def __init__(self, db: Any, collection_name: str = SCHEDULES_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, schedule: Schedule) -> dict[str, Any]:
        return schedule.model_dump(mode="json")

    def create(self, schedule: Schedule) -> Schedule:
        self._coll.document(schedule.id).set(self._dump(schedule))
        return schedule

    def get_by_id(self, id: str) -> Schedule | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Schedule.model_validate(doc.to_dict())

    def list(self, query_params: ScheduleQueryParams) -> list[Schedule]:
        query = self._coll
        query = apply_filters(query, query_params, ScheduleQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Schedule.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, schedule: Schedule) -> Schedule:
        self._coll.document(id).update(self._dump(schedule))
        return schedule

    def delete(self, id: str) -> None:
        self._coll.document(id).delete()
