from typing import Any

from domain.addresses.entity import Address, AddressQueryParams
from domain.addresses.repository import AddressRepository
from infrastructure.config import ADDRESSES_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters


class FirestoreAddressRepository(AddressRepository):
    def __init__(self, db: Any, collection_name: str = ADDRESSES_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, address: Address) -> dict[str, Any]:
        return address.model_dump(mode="json")

    def create(self, address: Address) -> Address:
        self._coll.document(address.id).set(self._dump(address))
        return address

    def get_by_id(self, id: str) -> Address | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Address.model_validate(doc.to_dict())

    def list(self, query_params: AddressQueryParams) -> list[Address]:
        query = self._coll
        query = apply_filters(query, query_params, AddressQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Address.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, address: Address) -> Address:
        self._coll.document(id).update(self._dump(address))
        return address

    def delete(self, id: str) -> None:
        self._coll.document(id).delete()
