from typing import Any

from google.cloud.firestore import DELETE_FIELD

from domain.invitations.entity import Invitation, InvitationQueryParams, InvitationStatus
from domain.invitations.repository import InvitationRepository
from infrastructure.config import INVITATIONS_COLLECTION_NAME
from infrastructure.persistence.firestore_common import apply_filters, get_timestamp


class FirestoreInvitationRepository(InvitationRepository):
    def __init__(self, db: Any, collection_name: str = INVITATIONS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, invitation: Invitation) -> dict[str, Any]:
        return invitation.model_dump(mode="json")

    def create(self, invitation: Invitation) -> Invitation:
        self._coll.document(invitation.id).set(self._dump(invitation))
        return invitation

    def get_by_id(self, id: str) -> Invitation | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return Invitation.model_validate(doc.to_dict())

    def list(self, query_params: InvitationQueryParams) -> list[Invitation]:
        query = self._coll
        query = apply_filters(query, query_params, InvitationQueryParams.FILTER_SPEC)
        if query_params.limit is not None:
            query = query.limit(query_params.limit)
        if query_params.offset is not None:
            query = query.offset(query_params.offset)
        snapshot = query.get()
        return [Invitation.model_validate(d.to_dict()) for d in snapshot]

    def update(self, id: str, invitation: Invitation) -> Invitation:
        payload = self._dump(invitation)
        payload["group_id"] = DELETE_FIELD
        self._coll.document(id).update(payload)
        return invitation

    def update_status(self, id: str, status: InvitationStatus, metadata: dict | None) -> Invitation | None:
        ref = self._coll.document(id)
        if not ref.get().exists:
            return None
        ref.update({"status": status.value, "updated_at": get_timestamp(), "metadata": metadata or {}})
        return self.get_by_id(id)

    def delete_by_id(self, id: str) -> None:
        self._coll.document(id).delete()
