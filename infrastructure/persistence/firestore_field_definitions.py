from typing import Any

from domain.field_definitions.entity import FieldDefinition, FieldDefinitionQueryParams
from domain.field_definitions.repository import FieldDefinitionRepository
from infrastructure.config import FIELD_DEFINITIONS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters


class FirestoreFieldDefinitionRepository(FieldDefinitionRepository):
    def __init__(self, db: Any, collection_name: str = FIELD_DEFINITIONS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, row: FieldDefinition) -> dict[str, Any]:
        return row.model_dump(mode="json")

    def create(self, row: FieldDefinition) -> FieldDefinition:
        self._coll.document(row.id).set(self._dump(row))
        return row

    def get_by_id(self, id: str) -> FieldDefinition | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return FieldDefinition.model_validate(doc.to_dict())

    def list(self, query_params: FieldDefinitionQueryParams) -> list[FieldDefinition]:
        query = self._coll
        query = apply_filters(query, query_params, FieldDefinitionQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [FieldDefinition.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, row: FieldDefinition) -> FieldDefinition:
        self._coll.document(id).set(self._dump(row))
        return row
