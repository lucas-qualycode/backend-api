from domain.inventory.entity import InventoryItem
from domain.products.entity import Product
from domain.products.types import inventory_document_id, inventory_product_type_field
from infrastructure.config import DEFAULT_INVENTORY_CURRENCY


def new_inventory_item_for_product(product: Product, now: str, currency: str | None = None) -> InventoryItem:
    cur = currency or DEFAULT_INVENTORY_CURRENCY
    meta: dict = {"parent_id": product.parent_id, "product_deleted": product.deleted}
    if product.parent_type:
        meta["parent_type"] = product.parent_type
    return InventoryItem(
        id=inventory_document_id(product.id),
        product_type=inventory_product_type_field(product.type),
        product_id=product.id,
        available_quantity=product.quantity,
        reserved_quantity=0,
        total_quantity=product.quantity,
        price=product.value,
        currency=cur,
        created_at=now,
        updated_at=now,
        metadata=meta,
    )


def inventory_update_dict_for_product(
    product: Product,
    current: InventoryItem,
    now: str,
) -> dict:
    reserved = current.reserved_quantity
    total = product.quantity
    available = max(0, total - reserved)
    meta = {
        **(current.metadata or {}),
        "active": product.active,
        "deleted": product.deleted,
        "parent_id": product.parent_id,
    }
    if product.parent_type:
        meta["parent_type"] = product.parent_type
    return {
        "price": product.value,
        "total_quantity": total,
        "available_quantity": available,
        "updated_at": now,
        "metadata": meta,
    }


def inventory_deactivate_update_dict(now: str, prior_metadata: dict | None) -> dict:
    meta = {**(prior_metadata or {}), "deleted": True, "deactivated_at": now}
    return {
        "available_quantity": 0,
        "updated_at": now,
        "metadata": meta,
    }
