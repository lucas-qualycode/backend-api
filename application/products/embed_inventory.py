from domain.inventory.entity import InventoryItem
from domain.inventory.repository import InventoryRepository

from application.products.inventory_resolve import resolve_inventory_for_product


def inventory_summary(inv: InventoryItem | None) -> dict | None:
    if inv is None:
        return None
    return {
        "id": inv.id,
        "available_quantity": inv.available_quantity,
        "reserved_quantity": inv.reserved_quantity,
        "total_quantity": inv.total_quantity,
    }


def embed_inventory_on_product_dicts(
    rows: list[dict],
    inventory_repo: InventoryRepository,
) -> list[dict]:
    for d in rows:
        pid = d.get("id")
        if not isinstance(pid, str):
            d["inventory"] = None
            continue
        inv = resolve_inventory_for_product(inventory_repo, pid)
        d["inventory"] = inventory_summary(inv)
    return rows


def embed_inventory_on_one_product_dict(
    row: dict,
    inventory_repo: InventoryRepository,
) -> dict:
    return embed_inventory_on_product_dicts([row], inventory_repo)[0]
