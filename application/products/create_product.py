import uuid

from backend_api.application.products.schemas import CreateProductInput
from backend_api.domain.products.entity import Product
from backend_api.domain.products.repository import ProductRepository


def create_product(
    repo: ProductRepository,
    data: CreateProductInput,
    created_by: str,
    now: str,
) -> Product:
    product = Product(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
        parent_type=data.parent_type,
        type=data.type,
        user_id=data.user_id,
        is_free=data.is_free,
        value=data.value,
        quantity=data.quantity,
        max_per_user=data.max_per_user,
        request_additional_info=data.request_additional_info,
        active=data.active,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
        metadata=data.metadata,
    )
    return repo.create(product)
