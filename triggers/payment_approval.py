import logging

from firebase_functions.core import Change
from firebase_functions.firestore_fn import Event, on_document_written
from google.cloud.firestore_v1 import DocumentSnapshot

from application.payments.process_payment_approval import process_payment_approval
from infrastructure.firebase import get_firestore_client
from infrastructure.persistence.firestore_invitations import FirestoreInvitationRepository
from infrastructure.persistence.firestore_orders import FirestoreOrderRepository
from infrastructure.persistence.firestore_payments import FirestorePaymentRepository
from infrastructure.persistence.firestore_products import FirestoreProductRepository
from infrastructure.persistence.firestore_user_products import FirestoreUserProductRepository

log = logging.getLogger("triggers.payment_approval")


@on_document_written(document="payments/{paymentId}")
def on_payment_status_changed(event: Event[Change[DocumentSnapshot | None]]) -> None:
    if event.data is None:
        return
    before = event.data.before.to_dict() if event.data.before else None
    after = event.data.after.to_dict() if event.data.after else None
    if after is None:
        log.info("Payment document deleted, skipping")
        return
    before_status = before.get("status") if before else None
    after_status = after.get("status")
    if before_status == "APPROVED" or after_status != "APPROVED":
        return
    payment_id = event.params.get("paymentId")
    if not payment_id:
        return
    log.info("Payment %s approved, processing products and invitation", payment_id)
    try:
        db = get_firestore_client()
        payment_repo = FirestorePaymentRepository(db)
        order_repo = FirestoreOrderRepository(db)
        product_repo = FirestoreProductRepository(db)
        user_product_repo = FirestoreUserProductRepository(db)
        invitation_repo = FirestoreInvitationRepository(db)
        process_payment_approval(
            payment_id=payment_id,
            payment_repo=payment_repo,
            order_repo=order_repo,
            product_repo=product_repo,
            user_product_repo=user_product_repo,
            invitation_repo=invitation_repo,
        )
        log.info("Successfully processed payment %s", payment_id)
    except Exception as e:
        log.exception("Error processing payment %s: %s", payment_id, e)
        raise
