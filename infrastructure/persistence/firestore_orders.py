from typing import Any

from domain.orders.entity import Order, OrderQueryParams
from domain.orders.repository import OrderRepository
from infrastructure.config import ORDERS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestoreOrderRepository(OrderRepository):
    def __init__(self, db: Any, collection_name: str = ORDERS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, order: Order) -> dict[str, Any]:
        return order.model_dump(mode="json")

    def create(self, order: Order) -> Order:
        self._coll.document(order.id).set(self._dump(order))
        return order

    def get_by_id(self, id: str) -> Order | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Order.model_validate(doc.to_dict())

    def list(self, query_params: OrderQueryParams) -> list[Order]:
        query = self._coll
        query = apply_filters(query, query_params, OrderQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Order.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, order: Order) -> Order:
        self._coll.document(id).update(self._dump(order))
        return order

    def update_status(self, id: str, status: str) -> Order | None:
        ref = self._coll.document(id)
        if not ref.get().exists:
            return None
        ref.update({"status": status, "updated_at": get_timestamp()})
        return self.get_by_id(id)
