from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from domain.taggings.entity import Tagging
from domain.taggings.repository import TaggingRepository
from infrastructure.config import TAGGINGS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters


def tagging_document_id(entity_type: str, entity_id: str, tag_id: str) -> str:
    return f"{entity_type}__{entity_id}__{tag_id}"


class FirestoreTaggingRepository(TaggingRepository):
    def __init__(self, db: Any, collection_name: str = TAGGINGS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def create(self, tagging: Tagging) -> Tagging:
        self._coll.document(tagging.id).set(tagging.model_dump(mode="json"))
        return tagging

    def list_by_entity(self, entity_type: str, entity_id: str) -> list[Tagging]:
        q = self._coll.where(filter=FieldFilter("entity_type", "==", entity_type)).where(
            filter=FieldFilter("entity_id", "==", entity_id),
        )
        return [Tagging.model_validate(d.to_dict()) for d in q.get()]

    def list_by_tag(
        self,
        entity_type: str,
        tag_id: str,
        limit: int | None,
        offset: int | None,
    ) -> list[Tagging]:
        q = (
            self._coll.where(filter=FieldFilter("entity_type", "==", entity_type))
            .where(filter=FieldFilter("tag_id", "==", tag_id))
            .order_by("created_at")
        )
        if offset is not None:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return [Tagging.model_validate(d.to_dict()) for d in q.get()]

    def list_for_entities(self, entity_type: str, entity_ids: list[str]) -> list[Tagging]:
        if not entity_ids:
            return []
        out: list[Tagging] = []
        for i in range(0, len(entity_ids), 10):
            chunk = entity_ids[i : i + 10]
            snap = (
                self._coll.where(filter=FieldFilter("entity_type", "==", entity_type))
                .where(filter=FieldFilter("entity_id", "in", chunk))
                .get()
            )
            out.extend(Tagging.model_validate(d.to_dict()) for d in snap)
        return out

    def delete_all_for_entity(self, entity_type: str, entity_id: str) -> None:
        batch = self._db.batch()
        n = 0
        for doc in (
            self._coll.where(filter=FieldFilter("entity_type", "==", entity_type))
            .where(filter=FieldFilter("entity_id", "==", entity_id))
            .stream()
        ):
            batch.delete(doc.reference)
            n += 1
            if n >= 450:
                batch.commit()
                batch = self._db.batch()
                n = 0
        if n:
            batch.commit()

    def replace_all_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        tag_ids: list[str],
        created_by: str,
        created_at: str,
    ) -> None:
        batch = self._db.batch()
        n = 0
        for doc in (
            self._coll.where(filter=FieldFilter("entity_type", "==", entity_type))
            .where(filter=FieldFilter("entity_id", "==", entity_id))
            .stream()
        ):
            batch.delete(doc.reference)
            n += 1
            if n >= 450:
                batch.commit()
                batch = self._db.batch()
                n = 0
        for tid in tag_ids:
            doc_id = tagging_document_id(entity_type, entity_id, tid)
            tg = Tagging(
                id=doc_id,
                tag_id=tid,
                entity_type=entity_type,
                entity_id=entity_id,
                created_by=created_by,
                created_at=created_at,
            )
            batch.set(self._coll.document(doc_id), tg.model_dump(mode="json"))
            n += 1
            if n >= 450:
                batch.commit()
                batch = self._db.batch()
                n = 0
        if n:
            batch.commit()
