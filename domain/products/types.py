from enum import StrEnum


class ProductType(StrEnum):
    TICKET = "TICKET"


class InventoryProductType(StrEnum):
    PRODUCT = "PRODUCT"
    TICKET = "TICKET"


def inventory_document_id(product_id: str) -> str:
    return f"PRODUCT_{product_id}"


def inventory_product_type_field(product_type: str | None) -> str:
    if product_type == ProductType.TICKET:
        return InventoryProductType.TICKET
    return InventoryProductType.PRODUCT
