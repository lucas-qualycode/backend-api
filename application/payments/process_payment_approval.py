import logging
from datetime import datetime, timezone

from backend_api.application.invitations import update_invitation_status
from backend_api.application.user_products import create_user_product
from backend_api.application.user_products.schemas import CreateUserProductInput
from backend_api.domain.orders.repository import OrderRepository
from backend_api.domain.payments.repository import PaymentRepository
from backend_api.domain.products.repository import ProductRepository
from backend_api.domain.invitations.repository import InvitationRepository
from backend_api.domain.user_products.repository import UserProductRepository

log = logging.getLogger("backend_api.process_payment_approval")


def process_payment_approval(
    payment_id: str,
    payment_repo: PaymentRepository,
    order_repo: OrderRepository,
    product_repo: ProductRepository,
    user_product_repo: UserProductRepository,
    invitation_repo: InvitationRepository,
) -> None:
    payment = payment_repo.get_by_id(payment_id)
    if not payment:
        log.warning("Payment %s not found", payment_id)
        return
    order = order_repo.get_by_id(payment.order_id)
    if not order:
        log.warning("Order %s not found for payment %s", payment.order_id, payment_id)
        return
    now = datetime.now(timezone.utc).isoformat()
    for item in order.items:
        product = product_repo.get_by_id(item.product_id)
        if not product:
            log.warning("Product %s not found", item.product_id)
            continue
        parent_id = (item.metadata or {}).get("parent_id") or product.parent_id
        if parent_id and product.parent_id != parent_id:
            log.warning("Product %s does not belong to parent %s", item.product_id, parent_id)
            continue
        invitation_id = (order.metadata or {}).get("invitation_id") if order.metadata else None
        base_metadata = {k: v for k, v in (item.metadata or {}).items() if k != "additional_data"}
        if invitation_id:
            base_metadata["invitation_id"] = invitation_id
        additional_list = (item.metadata or {}).get("additional_data") if isinstance((item.metadata or {}).get("additional_data"), list) else []
        for i in range(item.quantity):
            additional_data = additional_list[i] if i < len(additional_list) else {}
            data = CreateUserProductInput(
                parent_id=parent_id or "",
                product_id=item.product_id,
                user_id=payment.user_id,
                invitation_id=invitation_id,
                quantity=1,
                status="ACTIVE",
                purchase_date=now,
                valid_from=now,
                valid_until=getattr(product, "valid_until", None),
                price=product.value,
                currency=getattr(product, "currency", "BRL"),
                payment_id=payment_id,
                metadata=base_metadata,
                additional_data=additional_data,
            )
            create_user_product(user_product_repo, data, now)
    invitation_id = (order.metadata or {}).get("invitation_id") if order.metadata else None
    if invitation_id:
        invitation = invitation_repo.get_by_id(invitation_id)
        if invitation and invitation.status != "ACCEPTED":
            if invitation.status == "DECLINED":
                log.warning("Invitation %s is DECLINED, not updating to ACCEPTED", invitation_id)
            else:
                merged_metadata = {**(invitation.metadata or {}), "order_id": order.id, "payment_id": payment_id}
                if order.metadata and order.metadata.get("message") is not None:
                    merged_metadata["message"] = order.metadata["message"]
                update_invitation_status(invitation_repo, invitation_id, "ACCEPTED", merged_metadata)
