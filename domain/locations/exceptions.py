class LocationNotFoundError(Exception):
    def __init__(self, location_id: str) -> None:
        self.location_id = location_id
        super().__init__(f"Location not found: {location_id}")
