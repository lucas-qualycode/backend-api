from typing import Any

from google.cloud.firestore import DELETE_FIELD, transactional

from domain.invitation_guest_slots.entity import InvitationGuestSlot
from domain.invitations.entity import Invitation
from infrastructure.config import (
    INVITATION_GUEST_SLOTS_COLLECTION_NAME,
    INVITATIONS_COLLECTION_NAME,
)


def _invitation_update_payload(invitation: Invitation) -> dict[str, Any]:
    payload = invitation.model_dump(mode="json")
    payload["group_id"] = DELETE_FIELD
    return payload


@transactional
def _tx_update_invitation_guest_slots(
    transaction,
    db: Any,
    invitation_id: str,
    invitation: Invitation,
    slots: list[InvitationGuestSlot],
) -> None:
    inv_ref = db.collection(INVITATIONS_COLLECTION_NAME).document(invitation_id)
    sub = inv_ref.collection(INVITATION_GUEST_SLOTS_COLLECTION_NAME)
    existing_docs = list(sub.get(transaction=transaction))
    transaction.update(inv_ref, _invitation_update_payload(invitation))
    for doc in existing_docs:
        transaction.delete(doc.reference)
    for s in slots:
        transaction.set(sub.document(s.id), s.model_dump(mode="json"))


def run_update_invitation_with_guest_slots(
    db: Any,
    invitation_id: str,
    invitation: Invitation,
    slots: list[InvitationGuestSlot],
) -> None:
    transaction = db.transaction()
    _tx_update_invitation_guest_slots(transaction, db, invitation_id, invitation, slots)
