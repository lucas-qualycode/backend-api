from domain.invitations.entity import InvitationStatus
from utils.errors import ValidationError

_SENT_NEXT = frozenset({
    InvitationStatus.ACCEPTED,
    InvitationStatus.DECLINED,
    InvitationStatus.EXPIRED,
    InvitationStatus.CANCELLED,
})

_ALLOWED: dict[InvitationStatus, frozenset[InvitationStatus]] = {
    InvitationStatus.CREATED: _SENT_NEXT | frozenset({InvitationStatus.SENT}),
    InvitationStatus.SENT: _SENT_NEXT,
    InvitationStatus.ACCEPTED: frozenset({InvitationStatus.CANCELLED}),
    InvitationStatus.DECLINED: frozenset(),
    InvitationStatus.EXPIRED: frozenset({InvitationStatus.SENT}),
    InvitationStatus.CANCELLED: frozenset(),
}


def validate_invitation_status_transition(current: InvitationStatus, new: InvitationStatus) -> None:
    if current == new:
        return
    allowed = _ALLOWED.get(current, frozenset())
    if new not in allowed:
        raise ValidationError(
            f"Invalid invitation status transition: {current.value} → {new.value}",
        )
