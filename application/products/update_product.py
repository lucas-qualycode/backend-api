from typing import Any

from application.products.firestore_write import run_update_product_with_inventory
from application.products.schemas import UpdateProductInput
from application.products.validation import (
    validate_product_additional_info_fields_shape,
    validate_product_state,
    validate_product_update_patch,
)
from domain.products.entity import Product
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository


def update_product(
    db: Any,
    repo: ProductRepository,
    product_id: str,
    data: UpdateProductInput,
    last_updated_by: str,
    updated_at: str,
) -> Product:
    existing = repo.get_by_id(product_id)
    if existing is None:
        raise ProductNotFoundError(product_id)
    if existing.deleted:
        raise ProductNotFoundError(product_id)

    validate_product_update_patch(data)
    patch = data.model_dump(exclude_unset=True)
    if "additional_info_fields" in patch and data.additional_info_fields is not None:
        validate_product_additional_info_fields_shape(data.additional_info_fields)
    updates = data.model_dump(exclude_unset=True)
    updates.pop("tag_ids", None)
    updates.pop("user_id", None)
    if "additional_info_fields" in updates and "request_additional_info" not in updates:
        refs = updates["additional_info_fields"] or []
        updates["request_additional_info"] = len(refs) > 0
    if "imageURL" in updates:
        raw = updates["imageURL"]
        if raw is None:
            updates["imageURL"] = None
        else:
            s = str(raw).strip()
            updates["imageURL"] = s if s else None
    if updates.get("is_free") is True:
        updates["value"] = 0

    updated_product: Product = existing.model_copy(
        update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by}
    )
    if updated_product.is_free and updated_product.value != 0:
        updated_product = updated_product.model_copy(update={"value": 0})
    validate_product_state(updated_product)

    try:
        run_update_product_with_inventory(db, updated_product, updated_at)
    except ProductNotFoundError:
        raise ProductNotFoundError(product_id) from None
    return updated_product
