class InventoryNotFoundError(Exception):
    def __init__(self, inventory_id: str) -> None:
        self.inventory_id = inventory_id
        super().__init__(f"Inventory not found: {inventory_id}")
