from typing import Any, Literal

from pydantic import BaseModel, Field

from domain.payments.entity import PaymentStatus

PaymentNextAction = Literal["display_pix", "wait", "done", "failed"]


class PixDisplayPayload(BaseModel):
    qr_code_base64: str | None = None
    copy_paste_code: str | None = None
    ticket_url: str | None = None
    expires_at: str | None = None


class PaymentFailurePayload(BaseModel):
    code: str | None = None
    message: str | None = None


class MappedProviderPayment(BaseModel):
    payment_status: str
    payment_method: str | None = None
    next_action: PaymentNextAction
    pix: PixDisplayPayload | None = None
    failure: PaymentFailurePayload | None = None


_MP_APPROVED = frozenset({"approved", "accredited", "processed"})
_MP_PENDING = frozenset(
    {
        "pending",
        "in_process",
        "in_mediation",
        "action_required",
        "pending_waiting_transfer",
        "pending_contingency",
        "pending_review_manual",
        "created",
        "ready_to_process",
    }
)
_MP_PROCESSING = frozenset({"processing", "authorized"})
_MP_CANCELLED = frozenset({"cancelled", "expired"})
_MP_FAILED = frozenset({"rejected", "refunded", "charged_back", "failed"})


def _first_payment(response: dict[str, Any]) -> dict[str, Any] | None:
    transactions = response.get("transactions")
    if not isinstance(transactions, dict):
        return None
    payments = transactions.get("payments")
    if not isinstance(payments, list) or not payments:
        return None
    first = payments[0]
    return first if isinstance(first, dict) else None


def _normalize_method_id(raw: str | None) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    value = raw.strip().lower()
    if value == "pix":
        return "pix"
    if value in ("credit_card", "debit_card", "visa", "master", "elo", "amex"):
        return "card"
    if value:
        return value
    return None


def _extract_payment_method(payment: dict[str, Any] | None) -> str | None:
    if not payment:
        return None
    payment_method = payment.get("payment_method")
    if isinstance(payment_method, dict):
        method_id = payment_method.get("id")
        normalized = _normalize_method_id(method_id if isinstance(method_id, str) else None)
        if normalized:
            return normalized
        method_type = payment_method.get("type")
        if method_type == "bank_transfer":
            return "pix"
        if method_type in ("credit_card", "debit_card"):
            return "card"
    option_id = payment.get("payment_method_option_id")
    if isinstance(option_id, str):
        return _normalize_method_id(option_id)
    return None


def _map_mp_status(raw: str | None) -> str:
    if not raw:
        return PaymentStatus.PENDING
    key = raw.strip().lower()
    if key in _MP_APPROVED:
        return PaymentStatus.APPROVED
    if key in _MP_PROCESSING:
        return PaymentStatus.PROCESSING
    if key in _MP_CANCELLED:
        return PaymentStatus.CANCELLED
    if key in _MP_FAILED:
        return PaymentStatus.FAILED
    if key in _MP_PENDING:
        return PaymentStatus.PENDING
    return PaymentStatus.PENDING


def _pix_from_fields(
    *,
    qr_base64: Any,
    qr_code: Any,
    ticket_url: Any,
    expires_at: Any,
) -> PixDisplayPayload | None:
    copy_paste = qr_code if isinstance(qr_code, str) and qr_code.strip() else None
    if not any(
        isinstance(v, str) and v.strip()
        for v in (qr_base64, copy_paste, ticket_url, expires_at)
    ):
        return None
    return PixDisplayPayload(
        qr_code_base64=qr_base64 if isinstance(qr_base64, str) else None,
        copy_paste_code=copy_paste,
        ticket_url=ticket_url if isinstance(ticket_url, str) else None,
        expires_at=expires_at if isinstance(expires_at, str) else None,
    )


def _extract_pix_payload(payment: dict[str, Any] | None) -> PixDisplayPayload | None:
    if not payment:
        return None

    expires_at = payment.get("date_of_expiration") or payment.get("expiration_time")

    poi = payment.get("point_of_interaction")
    if isinstance(poi, dict):
        tx_data = poi.get("transaction_data")
        if isinstance(tx_data, dict):
            pix = _pix_from_fields(
                qr_base64=tx_data.get("qr_code_base64"),
                qr_code=tx_data.get("qr_code"),
                ticket_url=tx_data.get("ticket_url"),
                expires_at=tx_data.get("expiration_date")
                or tx_data.get("date_of_expiration")
                or expires_at,
            )
            if pix:
                return pix

    payment_method = payment.get("payment_method")
    if isinstance(payment_method, dict):
        pix = _pix_from_fields(
            qr_base64=payment_method.get("qr_code_base64"),
            qr_code=payment_method.get("qr_code"),
            ticket_url=payment_method.get("ticket_url"),
            expires_at=expires_at,
        )
        if pix:
            return pix

    return None


def _extract_failure(payment: dict[str, Any] | None) -> PaymentFailurePayload | None:
    if not payment:
        return None
    status = payment.get("status")
    if not isinstance(status, str):
        return None
    mapped = _map_mp_status(status)
    if mapped not in (PaymentStatus.FAILED, PaymentStatus.CANCELLED):
        return None
    detail = payment.get("status_detail")
    message = detail if isinstance(detail, str) and detail.strip() else status
    code = payment.get("status_detail")
    return PaymentFailurePayload(
        code=code if isinstance(code, str) else None,
        message=message,
    )


def _resolve_next_action(payment_status: str, payment_method: str | None, pix: PixDisplayPayload | None) -> PaymentNextAction:
    if payment_status == PaymentStatus.APPROVED:
        return "done"
    if payment_status in (PaymentStatus.FAILED, PaymentStatus.CANCELLED):
        return "failed"
    if payment_method == "pix" and pix is not None:
        return "display_pix"
    return "wait"


def map_provider_order_response(response: dict[str, Any]) -> MappedProviderPayment:
    payment = _first_payment(response)
    raw_status = None
    if payment and isinstance(payment.get("status"), str):
        raw_status = payment["status"]
    elif isinstance(response.get("status"), str):
        raw_status = response["status"]
    payment_status = _map_mp_status(raw_status)
    payment_method = _extract_payment_method(payment)
    pix = _extract_pix_payload(payment)
    failure = _extract_failure(payment)
    next_action = _resolve_next_action(payment_status, payment_method, pix)
    return MappedProviderPayment(
        payment_status=payment_status,
        payment_method=payment_method,
        next_action=next_action,
        pix=pix,
        failure=failure,
    )


def build_payment_outcome_from_stored(
    *,
    payment_status: str,
    payment_method: str | None,
    provider_response: dict[str, Any] | None,
) -> MappedProviderPayment:
    stored_method = _normalize_method_id(payment_method) if payment_method else None
    payment = _first_payment(provider_response) if provider_response else None
    pix = _extract_pix_payload(payment)
    failure = _extract_failure(payment) if payment else None
    resolved_method = stored_method
    if provider_response:
        mapped = map_provider_order_response(provider_response)
        if mapped.pix and not pix:
            pix = mapped.pix
        if mapped.failure and not failure:
            failure = mapped.failure
        if not resolved_method and mapped.payment_method:
            resolved_method = mapped.payment_method
        if mapped.payment_status != PaymentStatus.PENDING or payment_status == PaymentStatus.PENDING:
            next_action = _resolve_next_action(payment_status, resolved_method, pix)
            return MappedProviderPayment(
                payment_status=payment_status,
                payment_method=resolved_method,
                next_action=next_action,
                pix=pix,
                failure=failure,
            )
    next_action = _resolve_next_action(payment_status, resolved_method, pix)
    return MappedProviderPayment(
        payment_status=payment_status,
        payment_method=resolved_method,
        next_action=next_action,
        pix=pix,
        failure=failure,
    )
