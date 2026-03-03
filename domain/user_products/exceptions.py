class UserProductNotFoundError(Exception):
    def __init__(self, user_product_id: str) -> None:
        self.user_product_id = user_product_id
        super().__init__(f"User product not found: {user_product_id}")
