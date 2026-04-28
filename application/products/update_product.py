import logging
from typing import Any

from application.products.firestore_write import run_update_product_with_inventory
from application.products.schemas import UpdateProductInput
from application.products.validation import (
    validate_product_additional_info_fields_shape,
    validate_product_state,
    validate_product_update_patch,
)
from domain.products.entity import Product, ProductAdditionalInfoFieldRef
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository

log = logging.getLogger(__name__)


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

    log.info(
        "update_product start product_id=%s last_updated_by=%s type=%s",
        product_id,
        last_updated_by,
        existing.type,
    )
    try:
        validate_product_update_patch(data)
        patch = data.model_dump(exclude_unset=True)
        if "additional_info_fields" in patch and data.additional_info_fields is not None:
            validate_product_additional_info_fields_shape(data.additional_info_fields)
        updates = data.model_dump(exclude_unset=True)
        updates.pop("tag_ids", None)
        updates.pop("user_id", None)
        if "additional_info_fields" in updates:
            raw = updates["additional_info_fields"]
            refs = [] if raw is None else list(raw)
            updates["additional_info_fields"] = [
                ProductAdditionalInfoFieldRef.model_validate(r) for r in refs
            ]
        if "imageURL" in updates:
            raw = updates["imageURL"]
            if raw is None:
                updates["imageURL"] = None
            else:
                s = str(raw).strip()
                updates["imageURL"] = s if s else None
        if updates.get("is_free") is True:
            updates["value"] = 0

        log.info(
            "update_product patch_keys=%s additional_info_refs=%s",
            sorted(updates.keys()),
            len(updates.get("additional_info_fields", []) or []),
        )

        updated_product: Product = existing.model_copy(
            update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by}
        )
        if updated_product.is_free and updated_product.value != 0:
            updated_product = updated_product.model_copy(update={"value": 0})
        validate_product_state(updated_product)
    except Exception:
        log.exception(
            "update_product validate_or_merge_failed product_id=%s",
            product_id,
        )
        raise

    log.info(
        "update_product before_persist product_id=%s qty=%s value=%s is_free=%s active=%s",
        updated_product.id,
        updated_product.quantity,
        updated_product.value,
        updated_product.is_free,
        updated_product.active,
    )

    try:
        run_update_product_with_inventory(db, updated_product, updated_at)
    except ProductNotFoundError:
        raise ProductNotFoundError(product_id) from None
    except Exception:
        log.exception(
            "update_product persist_failed product_id=%s",
            product_id,
        )
        raise

    log.info("update_product ok product_id=%s", product_id)
    return updated_product
