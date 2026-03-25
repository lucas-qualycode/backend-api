from typing import Any

from domain.tags.entity import Tag, TagQueryParams
from domain.tags.repository import TagRepository
from infrastructure.config import TAGS_COLLECTION_NAME
from google.cloud.firestore_v1.base_query import FieldFilter

from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestoreTagRepository(TagRepository):
    def __init__(self, db: Any, collection_name: str = TAGS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def create(self, tag: Tag) -> Tag:
        self._coll.document(tag.id).set(tag.model_dump(mode="json"))
        return tag

    def get_by_id(self, id: str) -> Tag | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Tag.model_validate(doc.to_dict())

    def list(self, query_params: TagQueryParams) -> list[Tag]:
        query = self._coll
        if query_params.roots_only:
            query = query.where(filter=FieldFilter("parent_tag_id", "==", None))
            spec = [t for t in TagQueryParams.FILTER_SPEC if t[0] != "parent_tag_id"]
            query = apply_filters(query, query_params, spec)
        else:
            query = apply_filters(query, query_params, TagQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        return [Tag.model_validate(d.to_dict()) for d in query.get()]

    def update(self, id: str, tag: Tag) -> Tag:
        self._coll.document(id).set(tag.model_dump(mode="json"))
        return tag

    def soft_delete(self, id: str, last_updated_by: str) -> Tag | None:
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
