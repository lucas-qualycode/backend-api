from typing import Any

from application.products.firestore_write import run_soft_delete_product_with_inventory
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def delete_product(
    db: Any,
    repo: ProductRepository,
    tagging_repo: TaggingRepository,
    product_id: str,
    last_updated_by: str,
    now: str,
) -> None:
    existing = repo.get_by_id(product_id)
    if existing is None or existing.deleted:
        raise ProductNotFoundError(product_id)
    try:
        run_soft_delete_product_with_inventory(db, product_id, now, last_updated_by)
    except ProductNotFoundError:
        raise ProductNotFoundError(product_id) from None
    tagging_repo.delete_all_for_entity(TaggingEntityType.PRODUCT, product_id)
