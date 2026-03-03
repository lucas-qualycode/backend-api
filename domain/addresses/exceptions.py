class AddressNotFoundError(Exception):
    def __init__(self, address_id: str) -> None:
        self.address_id = address_id
        super().__init__(f"Address not found: {address_id}")
