from typing import Any

from google.cloud.firestore import transactional

from domain.invitation_guest_slots.entity import InvitationGuestSlot
from domain.invitations.entity import Invitation
from infrastructure.config import (
    INVITATION_GUEST_SLOTS_COLLECTION_NAME,
    INVITATIONS_COLLECTION_NAME,
)


@transactional
def _tx_create_invitation_with_slots(
    transaction,
    db: Any,
    invitation: Invitation,
    slots: list[InvitationGuestSlot],
) -> None:
    inv_ref = db.collection(INVITATIONS_COLLECTION_NAME).document(invitation.id)
    transaction.set(inv_ref, invitation.model_dump(mode="json"))
    sub = inv_ref.collection(INVITATION_GUEST_SLOTS_COLLECTION_NAME)
    for s in slots:
        transaction.set(sub.document(s.id), s.model_dump(mode="json"))


def run_create_invitation_with_guest_slots(
    db: Any,
    invitation: Invitation,
    slots: list[InvitationGuestSlot],
) -> None:
    transaction = db.transaction()
    _tx_create_invitation_with_slots(transaction, db, invitation, slots)
