from typing import Any

from google.cloud.firestore import transactional

from application.products.inventory_build import (
    inventory_deactivate_update_dict,
    inventory_update_dict_for_product,
    new_inventory_item_for_product,
)
from domain.inventory.entity import InventoryItem
from domain.products.entity import Product
from domain.products.exceptions import ProductNotFoundError
from domain.products.types import inventory_document_id, inventory_product_type_field
from infrastructure.config import (
    DEFAULT_INVENTORY_CURRENCY,
    INVENTORY_COLLECTION_NAME,
    PRODUCTS_COLLECTION_NAME,
)


@transactional
def _tx_create_product_inventory(
    transaction,
    db: Any,
    product: Product,
    inventory: InventoryItem,
) -> None:
    p_ref = db.collection(PRODUCTS_COLLECTION_NAME).document(product.id)
    i_ref = db.collection(INVENTORY_COLLECTION_NAME).document(inventory.id)
    transaction.set(p_ref, product.model_dump(mode="json"))
    transaction.set(i_ref, inventory.model_dump(mode="json"))


def run_create_product_with_inventory(db: Any, product: Product, inventory: InventoryItem) -> None:
    transaction = db.transaction()
    _tx_create_product_inventory(transaction, db, product, inventory)


@transactional
def _tx_update_product_inventory(
    transaction,
    db: Any,
    product: Product,
    now: str,
) -> None:
    p_ref = db.collection(PRODUCTS_COLLECTION_NAME).document(product.id)
    p_snap = p_ref.get(transaction=transaction)
    if not p_snap.exists:
        raise ProductNotFoundError(product.id)
    i_ref_p = db.collection(INVENTORY_COLLECTION_NAME).document(inventory_document_id(product.id))
    snap_p = i_ref_p.get(transaction=transaction)
    transaction.set(p_ref, product.model_dump(mode="json"))
    if snap_p.exists:
        current = InventoryItem.model_validate(snap_p.to_dict())
        upd = inventory_update_dict_for_product(product, current, now)
        upd["product_type"] = inventory_product_type_field(product.type)
        transaction.update(i_ref_p, upd)
        return

    inv = new_inventory_item_for_product(product, now, DEFAULT_INVENTORY_CURRENCY)
    transaction.set(i_ref_p, inv.model_dump(mode="json"))


def run_update_product_with_inventory(db: Any, product: Product, now: str) -> None:
    transaction = db.transaction()
    _tx_update_product_inventory(transaction, db, product, now)


@transactional
def _tx_soft_delete_product_inventory(
    transaction,
    db: Any,
    product_id: str,
    now: str,
    last_updated_by: str,
) -> None:
    p_ref = db.collection(PRODUCTS_COLLECTION_NAME).document(product_id)
    p_snap = p_ref.get(transaction=transaction)
    if not p_snap.exists:
        raise ProductNotFoundError(product_id)
    i_ref_p = db.collection(INVENTORY_COLLECTION_NAME).document(inventory_document_id(product_id))
    snap_p = i_ref_p.get(transaction=transaction)
    transaction.update(
        p_ref,
        {"deleted": True, "updated_at": now, "last_updated_by": last_updated_by},
    )
    if snap_p.exists:
        meta = snap_p.to_dict().get("metadata")
        if isinstance(meta, dict):
            patch = inventory_deactivate_update_dict(now, meta)
        else:
            patch = inventory_deactivate_update_dict(now, None)
        transaction.update(i_ref_p, patch)


def run_soft_delete_product_with_inventory(
    db: Any,
    product_id: str,
    now: str,
    last_updated_by: str,
) -> None:
    transaction = db.transaction()
    _tx_soft_delete_product_inventory(transaction, db, product_id, now, last_updated_by)
