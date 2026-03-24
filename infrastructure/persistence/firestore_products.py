from typing import Any

from domain.products.entity import Product, ProductQueryParams
from domain.products.repository import ProductRepository
from infrastructure.config import PRODUCTS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters


class FirestoreProductRepository(ProductRepository):
    def __init__(self, db: Any, collection_name: str = PRODUCTS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, product: Product) -> dict[str, Any]:
        return product.model_dump(mode="json")

    def create(self, product: Product) -> Product:
        self._coll.document(product.id).set(self._dump(product))
        return product

    def get_by_id(self, id: str) -> Product | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Product.model_validate(doc.to_dict())

    def list(self, query_params: ProductQueryParams) -> list[Product]:
        query = self._coll
        query = apply_filters(query, query_params, ProductQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Product.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, product: Product) -> Product:
        self._coll.document(id).update(self._dump(product))
        return product

    def soft_delete(self, id: str) -> None:
        self._coll.document(id).update({"deleted": True})
