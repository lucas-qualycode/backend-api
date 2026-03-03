import uuid

from backend_api.application.user_products.schemas import CreateUserProductInput
from backend_api.domain.user_products.entity import UserProduct
from backend_api.domain.user_products.repository import UserProductRepository


def create_user_product(
    repo: UserProductRepository,
    data: CreateUserProductInput,
    now: str,
) -> UserProduct:
    user_product = UserProduct(
        id=str(uuid.uuid4()),
        parent_id=data.parent_id,
        product_id=data.product_id,
        user_id=data.user_id,
        invitation_id=data.invitation_id,
        quantity=data.quantity,
        status=data.status,
        purchase_date=data.purchase_date,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        price=data.price,
        currency=data.currency,
        payment_id=data.payment_id,
        created_at=now,
        updated_at=now,
        metadata=data.metadata,
        additional_data=data.additional_data,
    )
    return repo.create(user_product)
