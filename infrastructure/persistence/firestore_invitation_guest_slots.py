from typing import Any

from domain.invitation_guest_slots.entity import InvitationGuestSlot
from domain.invitation_guest_slots.repository import InvitationGuestSlotRepository
from infrastructure.config import INVITATION_GUEST_SLOTS_COLLECTION_NAME, INVITATIONS_COLLECTION_NAME


class FirestoreInvitationGuestSlotRepository(InvitationGuestSlotRepository):
    def __init__(
        self,
        db: Any,
        invitations_collection: str = INVITATIONS_COLLECTION_NAME,
        slots_collection: str = INVITATION_GUEST_SLOTS_COLLECTION_NAME,
    ) -> None:
        self._db = db
        self._invitations_collection = invitations_collection
        self._slots_collection = slots_collection

    def _sub(self, invitation_id: str):
        return (
            self._db.collection(self._invitations_collection)
            .document(invitation_id)
            .collection(self._slots_collection)
        )

    def list_by_invitation_id(self, invitation_id: str) -> list[InvitationGuestSlot]:
        snapshot = self._sub(invitation_id).get()
        rows = [InvitationGuestSlot.model_validate(d.to_dict()) for d in snapshot]
        return sorted(rows, key=lambda s: (s.created_at, s.id))

    def delete_all_for_invitation(self, invitation_id: str) -> None:
        batch = self._db.batch()
        n = 0
        for doc in self._sub(invitation_id).stream():
            batch.delete(doc.reference)
            n += 1
            if n >= 450:
                batch.commit()
                batch = self._db.batch()
                n = 0
        if n:
            batch.commit()
