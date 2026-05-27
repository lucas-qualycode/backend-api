import json
import logging
import os
import urllib.error
import urllib.request

from infrastructure.config import (
    MERCADOPAGO_ACCESS_TOKEN_ENV,
    MERCADOPAGO_API_BASE_URL_ENV,
    MERCADOPAGO_DEFAULT_API_BASE_URL,
)
from utils.errors import ValidationError

logger = logging.getLogger(__name__)


class MercadoPagoApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None, body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _access_token() -> str:
    token = (os.environ.get(MERCADOPAGO_ACCESS_TOKEN_ENV) or "").strip()
    if not token:
        raise ValidationError("Mercado Pago is not configured")
    return token


def _api_base_url() -> str:
    raw = (os.environ.get(MERCADOPAGO_API_BASE_URL_ENV) or "").strip()
    return (raw or MERCADOPAGO_DEFAULT_API_BASE_URL).rstrip("/")


def _credential_kind() -> str:
    token = (os.environ.get(MERCADOPAGO_ACCESS_TOKEN_ENV) or "").strip()
    if token.startswith("TEST-"):
        return "TEST"
    if token.startswith("APP_USR-"):
        return "APP_USR"
    if token:
        return "unknown_prefix"
    return "missing"


def _parse_mp_error_detail(body: str) -> str | None:
    if not body.strip():
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return body.strip()[:500]
    if not isinstance(data, dict):
        return body.strip()[:500]
    for key in ("message", "error", "status_detail"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    errors = data.get("errors") or data.get("cause")
    if isinstance(errors, list) and errors:
        first = errors[0]
        if isinstance(first, dict):
            for key in ("message", "description", "code"):
                value = first.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        if isinstance(first, str) and first.strip():
            return first.strip()
    return body.strip()[:500]


def create_order(provider_checkout: dict, *, idempotency_key: str | None = None) -> dict:
    url = f"{_api_base_url()}/v1/orders"
    payload = json.dumps(provider_checkout).encode("utf-8")
    mp_idempotency = (
        idempotency_key
        or provider_checkout.get("external_reference")
        or ""
    )
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {_access_token()}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(mp_idempotency),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            if not body:
                return {}
            parsed = json.loads(body)
            if not isinstance(parsed, dict):
                raise MercadoPagoApiError("Unexpected Mercado Pago response")
            return parsed
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        detail = _parse_mp_error_detail(err_body)
        logger.error(
            "Mercado Pago POST %s failed: status=%s credential=%s idempotency_key=%s detail=%s body=%s",
            url,
            exc.code,
            _credential_kind(),
            mp_idempotency or "<empty>",
            detail or "<empty>",
            err_body,
        )
        message = f"Mercado Pago request failed ({exc.code})"
        if detail:
            message = f"{message}: {detail}"
        raise MercadoPagoApiError(
            message,
            status_code=exc.code,
            body=err_body,
        ) from exc
    except urllib.error.URLError as exc:
        logger.error("Mercado Pago POST %s failed: %s", url, exc.reason)
        raise MercadoPagoApiError(f"Mercado Pago request failed: {exc.reason}") from exc


def extract_provider_order_id(response: dict) -> str | None:
    order_id = response.get("id")
    if isinstance(order_id, str) and order_id.strip():
        return order_id.strip()
    return None
