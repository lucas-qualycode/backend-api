from typing import Any

from application.orders.schemas import InvitationCheckoutResponse
from application.orders.checkout_validation import (
    assert_total_cents_matches,
    validate_and_build_order_items,
)
from application.orders.create_order import create_order
from application.orders.schemas import CreateOrderInput, InvitationCheckoutRequest, OrderItemInput
from application.payments.create_payment import create_payment
from application.payments.schemas import CreatePaymentInput
from application.invitations.payment_outcome import (
    apply_mapped_status_to_payment,
    build_checkout_response,
    map_stored_provider_response,
)
from domain.invitations.entity import Invitation
from domain.orders.repository import OrderRepository
from domain.payments.entity import PaymentStatus
from domain.payments.repository import PaymentRepository
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository
from infrastructure.mercadopago import client as mp_client
from infrastructure.mercadopago.client import MercadoPagoApiError
from infrastructure.mercadopago.order_response import (
    build_payment_outcome_from_stored,
    map_provider_order_response,
)
from infrastructure.persistence.firestore_checkout_intents import FirestoreCheckoutIntentRepository
from utils.errors import ValidationError


def guest_user_id(invitation_id: str) -> str:
    return f"guest:{invitation_id}"


def extract_payer_email(provider_checkout: dict[str, Any]) -> str | None:
    payer = provider_checkout.get("payer")
    if not isinstance(payer, dict):
        return None
    email = payer.get("email")
    if isinstance(email, str) and email.strip():
        return email.strip()
    return None


def extract_payment_method(provider_checkout: dict[str, Any]) -> str | None:
    transactions = provider_checkout.get("transactions")
    if not isinstance(transactions, dict):
        return None
    payments = transactions.get("payments")
    if not isinstance(payments, list) or not payments:
        return None
    first = payments[0]
    if not isinstance(first, dict):
        return None
    payment_method = first.get("payment_method")
    if not isinstance(payment_method, dict):
        return None
    method_id = payment_method.get("id")
    if isinstance(method_id, str) and method_id.strip():
        return method_id.strip()
    return None


def _response_from_intent(intent: dict[str, Any]) -> InvitationCheckoutResponse:
    response = intent.get("response")
    if isinstance(response, dict):
        return InvitationCheckoutResponse.model_validate(response)
    return InvitationCheckoutResponse(
        order_id=str(intent.get("order_id", "")),
        payment_id=str(intent.get("payment_id", "")),
        payment_provider_payment_id=intent.get("payment_provider_payment_id"),
        idempotent_replay=True,
    )


def process_invitation_checkout(
    invitation: Invitation,
    data: InvitationCheckoutRequest,
    *,
    idempotency_key: str,
    order_repo: OrderRepository,
    payment_repo: PaymentRepository,
    product_repo: ProductRepository,
    checkout_intent_repo: FirestoreCheckoutIntentRepository,
    now: str,
) -> InvitationCheckoutResponse:
    inv_id = invitation.id
    if data.invitation_id and data.invitation_id != inv_id:
        raise ValidationError("invitation_id does not match invitation")
    if (data.parent_id or "") != invitation.event_id:
        raise ValidationError("parent_id does not match invitation event")

    existing = checkout_intent_repo.get(inv_id, idempotency_key)
    if existing and existing.get("status") == checkout_intent_repo.STATUS_COMPLETED:
        return _response_from_intent(existing)

    started = checkout_intent_repo.try_start_processing(inv_id, idempotency_key)
    if not started:
        existing = checkout_intent_repo.get(inv_id, idempotency_key)
        if existing and existing.get("status") == checkout_intent_repo.STATUS_COMPLETED:
            return _response_from_intent(existing)
        if existing and existing.get("status") == "failed":
            if not checkout_intent_repo.retry_after_failure(inv_id, idempotency_key):
                raise ValidationError("Checkout could not be retried")
        else:
            raise ValidationError("Checkout is already in progress for this idempotency key")

    try:
        validated_items, subtotal = validate_and_build_order_items(
            product_repo,
            data.items,
            invitation.event_id,
        )
        assert_total_cents_matches(subtotal, data.total_cents)

        payer_email = extract_payer_email(data.provider_checkout)
        order_metadata: dict[str, Any] = dict(data.metadata)
        if payer_email:
            order_metadata["payer_email"] = payer_email
        order_metadata["idempotency_key"] = idempotency_key

        user_id = guest_user_id(inv_id)
        order = create_order(
            order_repo,
            CreateOrderInput(
                user_id=user_id,
                parent_id=invitation.event_id,
                invitation_id=inv_id,
                items=validated_items,
                currency=data.currency,
                metadata=order_metadata,
                expires_at=data.expires_at,
                payment_provider=data.payment_provider,
            ),
            now,
        )

        payment_method = extract_payment_method(data.provider_checkout)
        payment_metadata: dict[str, Any] = {"idempotency_key": idempotency_key}
        if payer_email:
            payment_metadata["payer_email"] = payer_email

        payment = create_payment(
            payment_repo,
            CreatePaymentInput(
                order_id=order.id,
                user_id=user_id,
                amount=order.total_amount,
                currency=order.currency,
                status=PaymentStatus.PENDING,
                payment_provider=data.payment_provider,
                payment_method=payment_method,
                metadata=payment_metadata,
            ),
            now,
        )

        provider_order_id: str | None = None
        provider_response: dict[str, Any] = {}
        mapped = map_stored_provider_response(None)

        if order.total_amount > 0:
            provider_body = dict(data.provider_checkout)
            provider_body.setdefault(
                "external_reference",
                f"inv_{inv_id}_order_{order.id}",
            )
            try:
                provider_response = mp_client.create_order(
                    provider_body,
                    idempotency_key=idempotency_key,
                )
                provider_order_id = mp_client.extract_provider_order_id(provider_response)
                mapped = map_provider_order_response(provider_response)
                if (
                    mapped.pix is None
                    and provider_order_id
                    and (payment_method == "pix" or mapped.payment_method == "pix")
                ):
                    try:
                        provider_response = mp_client.get_order(provider_order_id)
                        mapped = build_payment_outcome_from_stored(
                            payment_status=mapped.payment_status,
                            payment_method="pix",
                            provider_response=provider_response,
                        )
                    except (MercadoPagoApiError, ValidationError):
                        pass
            except (MercadoPagoApiError, ValidationError) as exc:
                failed_payment = payment.model_copy(
                    update={
                        "status": PaymentStatus.FAILED,
                        "metadata": {
                            **payment.metadata,
                            "provider_error": str(exc),
                        },
                        "updated_at": now,
                    }
                )
                payment_repo.update(payment.id, failed_payment)
                checkout_intent_repo.fail(inv_id, idempotency_key, error=str(exc))
                raise

            payment = apply_mapped_status_to_payment(payment, mapped, now)
            payment = payment.model_copy(
                update={
                    "payment_provider_payment_id": provider_order_id,
                    "payment_method": payment_method or mapped.payment_method,
                    "metadata": {
                        **payment.metadata,
                        "provider_response": provider_response,
                    },
                    "updated_at": now,
                }
            )
            payment_repo.update(payment.id, payment)
        else:
            payment = payment.model_copy(
                update={
                    "status": PaymentStatus.APPROVED,
                    "updated_at": now,
                }
            )
            payment_repo.update(payment.id, payment)
            mapped = mapped.model_copy(
                update={
                    "payment_status": PaymentStatus.APPROVED,
                    "next_action": "done",
                }
            )

        api_response = build_checkout_response(
            order_id=order.id,
            payment_id=payment.id,
            payment_provider_payment_id=provider_order_id,
            mapped=mapped,
            total_cents=order.total_amount,
            idempotent_replay=False,
        )
        checkout_intent_repo.complete(
            inv_id,
            idempotency_key,
            order_id=order.id,
            payment_id=payment.id,
            payment_provider_payment_id=provider_order_id,
            response_payload=api_response.model_dump(mode="json"),
        )
        return api_response
    except ProductNotFoundError:
        checkout_intent_repo.fail(inv_id, idempotency_key, error="product_not_found")
        raise
    except ValidationError as exc:
        checkout_intent_repo.fail(inv_id, idempotency_key, error=str(exc.message))
        raise
