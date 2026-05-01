class ProductNotFoundError(Exception):
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Product not found: {product_id}")


class ProductDeleteBlockedError(Exception):
    def __init__(self, reason_code: str = "PRODUCT_HAS_INVITATIONS") -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)
