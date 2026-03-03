class AttendeeNotFoundError(Exception):
    def __init__(self, attendee_id: str) -> None:
        self.attendee_id = attendee_id
        super().__init__(f"Attendee not found: {attendee_id}")
