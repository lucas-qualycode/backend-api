from typing import Any

from domain.payments.entity import Payment, PaymentQueryParams
from domain.payments.repository import PaymentRepository
from infrastructure.config import PAYMENTS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestorePaymentRepository(PaymentRepository):
    def __init__(self, db: Any) -> None:
        self._db = db
        self._coll = db.collection(PAYMENTS_COLLECTION_NAME)

    def _dump(self, payment: Payment) -> dict[str, Any]:
        return payment.model_dump(mode="json")

    def create(self, payment: Payment) -> Payment:
        self._coll.document(payment.id).set(self._dump(payment))
        return payment

    def get_by_id(self, id: str) -> Payment | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Payment.model_validate(doc.to_dict())

    def list(self, query_params: PaymentQueryParams) -> list[Payment]:
        query = self._coll
        query = apply_filters(query, query_params, PaymentQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Payment.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, payment: Payment) -> Payment:
        self._coll.document(id).update(self._dump(payment))
        return payment

    def update_status(self, id: str, status: str) -> Payment | None:
        ref = self._coll.document(id)
        if not ref.get().exists:
            return None
        ref.update({"status": status, "updated_at": get_timestamp()})
        return self.get_by_id(id)
