from typing import Any

from google.api_core.exceptions import AlreadyExists

from infrastructure.config import CHECKOUT_INTENTS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import get_timestamp


class FirestoreCheckoutIntentRepository:
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"

    def __init__(self, db: Any, collection_name: str = CHECKOUT_INTENTS_COLLECTION_NAME) -> None:
        self._coll = db.collection(collection_name)

    @staticmethod
    def document_id(invitation_id: str, idempotency_key: str) -> str:
        safe_key = idempotency_key.strip().replace("/", "_")
        return f"{invitation_id}__{safe_key}"

    def get(self, invitation_id: str, idempotency_key: str) -> dict[str, Any] | None:
        doc = self._coll.document(self.document_id(invitation_id, idempotency_key)).get()
        if not doc.exists:
            return None
        data = doc.to_dict() or {}
        data["id"] = doc.id
        return data

    def try_start_processing(self, invitation_id: str, idempotency_key: str) -> bool:
        ref = self._coll.document(self.document_id(invitation_id, idempotency_key))
        now = get_timestamp()
        try:
            ref.create(
                {
                    "invitation_id": invitation_id,
                    "idempotency_key": idempotency_key,
                    "status": self.STATUS_PROCESSING,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            return True
        except AlreadyExists:
            return False

    def retry_after_failure(self, invitation_id: str, idempotency_key: str) -> bool:
        ref = self._coll.document(self.document_id(invitation_id, idempotency_key))
        doc = ref.get()
        if not doc.exists:
            return False
        data = doc.to_dict() or {}
        if data.get("status") != "failed":
            return False
        ref.update(
            {
                "status": self.STATUS_PROCESSING,
                "error": None,
                "updated_at": get_timestamp(),
            }
        )
        return True

    def complete(
        self,
        invitation_id: str,
        idempotency_key: str,
        *,
        order_id: str,
        payment_id: str,
        payment_provider_payment_id: str | None,
        response_payload: dict[str, Any],
    ) -> None:
        ref = self._coll.document(self.document_id(invitation_id, idempotency_key))
        ref.set(
            {
                "status": self.STATUS_COMPLETED,
                "order_id": order_id,
                "payment_id": payment_id,
                "payment_provider_payment_id": payment_provider_payment_id,
                "response": response_payload,
                "updated_at": get_timestamp(),
            },
            merge=True,
        )

    def fail(self, invitation_id: str, idempotency_key: str, *, error: str) -> None:
        ref = self._coll.document(self.document_id(invitation_id, idempotency_key))
        ref.set(
            {
                "status": "failed",
                "error": error,
                "updated_at": get_timestamp(),
            },
            merge=True,
        )
