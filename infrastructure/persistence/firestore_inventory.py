from typing import Any

from backend_api.domain.inventory.entity import InventoryItem
from backend_api.domain.inventory.repository import InventoryRepository
from backend_api.infrastructure.config import INVENTORY_COLLECTION_NAME
from backend_api.infrastructure.persistence.firestore_common import get_timestamp


class FirestoreInventoryRepository(InventoryRepository):
    def __init__(self, db: Any, collection_name: str = INVENTORY_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, item: InventoryItem) -> dict[str, Any]:
        return item.model_dump(mode="json")

    def get_by_id(self, id: str) -> InventoryItem | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return InventoryItem.model_validate(doc.to_dict())

    def create(self, item: InventoryItem) -> InventoryItem:
        self._coll.document(item.id).set(self._dump(item))
        return item

    def update(self, id: str, updates: dict) -> InventoryItem | None:
        ref = self._coll.document(id)
        doc = ref.get()
        if not doc.exists:
            return None
        ref.update({**updates, "updated_at": get_timestamp()})
        return self.get_by_id(id)

    def reserve(self, id: str, quantity: int) -> bool:
        ref = self._coll.document(id)
        doc = ref.get()
        if not doc.exists:
            return False
        data = doc.to_dict()
        available = data.get("available_quantity", 0)
        reserved = data.get("reserved_quantity", 0)
        if available < quantity:
            return False
        ref.update({
            "available_quantity": available - quantity,
            "reserved_quantity": reserved + quantity,
            "updated_at": get_timestamp(),
        })
        return True

    def release(self, id: str, quantity: int) -> bool:
        ref = self._coll.document(id)
        doc = ref.get()
        if not doc.exists:
            return False
        data = doc.to_dict()
        available = data.get("available_quantity", 0)
        reserved = data.get("reserved_quantity", 0)
        if reserved < quantity:
            return False
        ref.update({
            "available_quantity": available + quantity,
            "reserved_quantity": reserved - quantity,
            "updated_at": get_timestamp(),
        })
        return True
