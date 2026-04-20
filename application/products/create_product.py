import uuid
from typing import Any

from application.products.firestore_write import run_create_product_with_inventory
from application.products.inventory_build import new_inventory_item_for_product
from application.products.schemas import CreateProductInput
from application.products.validation import (
    validate_product_additional_info_fields_shape,
    validate_product_create,
)
from domain.products.entity import Product
from infrastructure.config import DEFAULT_INVENTORY_CURRENCY


def create_product(
    db: Any,
    data: CreateProductInput,
    created_by: str,
    now: str,
) -> Product:
    validate_product_create(data)
    validate_product_additional_info_fields_shape(data.additional_info_fields)
    value = 0 if data.is_free else data.value
    has_additional = len(data.additional_info_fields) > 0
    product = Product(
        id=str(uuid.uuid4()),
        name=data.name.strip(),
        description=str(data.description).strip(),
        imageURL=(data.imageURL.strip() if data.imageURL and str(data.imageURL).strip() else None),
        parent_id=data.parent_id,
        parent_type=data.parent_type,
        type=data.type,
        fulfillment_type=data.fulfillment_type,
        fulfillment_profile_id=data.fulfillment_profile_id,
        user_id=created_by,
        is_free=data.is_free,
        value=value,
        quantity=data.quantity,
        max_per_user=data.max_per_user,
        request_additional_info=has_additional,
        additional_info_fields=data.additional_info_fields,
        active=data.active,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
        metadata=data.metadata,
    )
    inventory = new_inventory_item_for_product(product, now, DEFAULT_INVENTORY_CURRENCY)
    run_create_product_with_inventory(db, product, inventory)
    return product
