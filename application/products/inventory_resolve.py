from domain.inventory.entity import InventoryItem
from domain.inventory.repository import InventoryRepository
from domain.products.types import inventory_document_id


def resolve_inventory_for_product(
    inventory_repo: InventoryRepository,
    product_id: str,
) -> InventoryItem | None:
    return inventory_repo.get_by_id(inventory_document_id(product_id))
