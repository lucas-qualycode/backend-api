from typing import Any

from domain.user_products.entity import UserProduct, UserProductQueryParams
from domain.user_products.repository import UserProductRepository
from infrastructure.config import USER_PRODUCTS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestoreUserProductRepository(UserProductRepository):
    def __init__(self, db: Any, collection_name: str = USER_PRODUCTS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, user_product: UserProduct) -> dict[str, Any]:
        return user_product.model_dump(mode="json")

    def create(self, user_product: UserProduct) -> UserProduct:
        self._coll.document(user_product.id).set(self._dump(user_product))
        return user_product

    def get_by_id(self, id: str) -> UserProduct | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return UserProduct.model_validate(doc.to_dict())

    def list(self, query_params: UserProductQueryParams) -> list[UserProduct]:
        query = self._coll
        query = apply_filters(query, query_params, UserProductQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [UserProduct.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, user_product: UserProduct) -> UserProduct:
        self._coll.document(id).update(self._dump(user_product))
        return user_product

    def update_status(self, id: str, status: str) -> UserProduct | None:
        ref = self._coll.document(id)
        if not ref.get().exists:
            return None
        ref.update({"status": status, "updated_at": get_timestamp()})
        return self.get_by_id(id)
