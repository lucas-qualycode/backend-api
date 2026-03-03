class InvitationNotFoundError(Exception):
    def __init__(self, invitation_id: str) -> None:
        self.invitation_id = invitation_id
        super().__init__(f"Invitation not found: {invitation_id}")
