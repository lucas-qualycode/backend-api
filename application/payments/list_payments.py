from backend_api.domain.payments.entity import Payment, PaymentQueryParams
from backend_api.domain.payments.repository import PaymentRepository


def list_payments(
    repo: PaymentRepository,
    query_params: PaymentQueryParams,
) -> list[Payment]:
    return repo.list(query_params)
