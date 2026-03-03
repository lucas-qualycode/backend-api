class StandNotFoundError(Exception):
    def __init__(self, stand_id: str) -> None:
        self.stand_id = stand_id
        super().__init__(f"Stand not found: {stand_id}")
