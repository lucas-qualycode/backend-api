import pytest
from fastapi import HTTPException

from api.auth import CurrentUser
from api.invitation_access import require_event_product_list_access
from domain.events.entity import Event


class _EventRepo:
    def __init__(self, event: Event | None) -> None:
        self._event = event

    def get_by_id(self, _id: str):
        return self._event


def _event(created_by: str = "owner-1") -> Event:
    return Event(
        id="evt-1",
        name="Test",
        active=True,
        is_paid=False,
        is_online=False,
        created_by=created_by,
        last_updated_by=created_by,
        visibility="private",
        deleted=False,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


def test_require_event_product_list_access_allows_without_parent_id():
    require_event_product_list_access(
        user=None,
        parent_id=None,
        event_repo=_EventRepo(None),
    )


def test_require_event_product_list_access_requires_owner_for_parent_id():
    user = CurrentUser(uid="owner-1")
    require_event_product_list_access(
        user=user,
        parent_id="evt-1",
        event_repo=_EventRepo(_event()),
    )


def test_require_event_product_list_access_rejects_anonymous_parent_id():
    with pytest.raises(HTTPException) as exc:
        require_event_product_list_access(
            user=None,
            parent_id="evt-1",
            event_repo=_EventRepo(_event()),
        )
    assert exc.value.status_code == 404


def test_require_event_product_list_access_rejects_non_owner():
    user = CurrentUser(uid="other-user")
    with pytest.raises(HTTPException) as exc:
        require_event_product_list_access(
            user=user,
            parent_id="evt-1",
            event_repo=_EventRepo(_event()),
        )
    assert exc.value.status_code == 404
