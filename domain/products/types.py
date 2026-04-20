from enum import StrEnum


class ProductType(StrEnum):
    TICKET = "TICKET"
    MERCH = "MERCH"


class FulfillmentType(StrEnum):
    DIGITAL = "DIGITAL"
    WILL_CALL = "WILL_CALL"
    SHIPPING = "SHIPPING"
    PICKUP = "PICKUP"


class InventoryProductType(StrEnum):
    PRODUCT = "PRODUCT"
    TICKET = "TICKET"


def inventory_document_id(product_id: str) -> str:
    return f"PRODUCT_{product_id}"


def inventory_product_type_field(product_type: ProductType | str | None) -> str:
    if product_type == ProductType.TICKET or product_type == "TICKET":
        return InventoryProductType.TICKET
    return InventoryProductType.PRODUCT
