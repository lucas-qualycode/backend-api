class EventTypeNotFoundError(Exception):
    def __init__(self, event_type_id: str) -> None:
        self.event_type_id = event_type_id
        super().__init__(f"Event type not found: {event_type_id}")
