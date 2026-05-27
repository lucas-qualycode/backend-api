import time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request

from api.field_definitions_public import (
    PUBLIC_LIST_QUERY,
    _check_rate_limit,
    assert_public_readable,
    rate_limit_field_definitions_read,
    resolve_list_query_params,
    serialize_field_definition,
)
from api.auth import CurrentUser
from domain.field_definitions.entity import FieldDefinition, FieldType
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError


def _row(**kwargs) -> FieldDefinition:
    base = {
        "id": "fd-1",
        "key": "email",
        "label": "Email",
        "field_type": FieldType.TEXT,
        "active": True,
        "deleted": False,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "created_by": "user-1",
        "last_updated_by": "user-1",
    }
    base.update(kwargs)
    return FieldDefinition(**base)


def test_resolve_list_query_params_public_defaults():
    params, public = resolve_list_query_params(
        None,
        active=None,
        deleted=None,
        field_type=None,
        limit=None,
        offset=None,
    )
    assert public is True
    assert params == PUBLIC_LIST_QUERY


def test_resolve_list_query_params_public_rejects_extra_filters():
    with pytest.raises(HTTPException) as exc:
        resolve_list_query_params(
            None,
            active=False,
            deleted=None,
            field_type=None,
            limit=None,
            offset=None,
        )
    assert exc.value.status_code == 400


def test_resolve_list_query_params_authenticated_allows_filters():
    user = CurrentUser(uid="org-1")
    params, public = resolve_list_query_params(
        user,
        active=False,
        deleted=True,
        field_type=FieldType.TEXT,
        limit=10,
        offset=5,
    )
    assert public is False
    assert params.active is False
    assert params.deleted is True
    assert params.field_type == FieldType.TEXT
    assert params.limit == 10
    assert params.offset == 5


def test_serialize_field_definition_public_strips_audit_fields():
    data = serialize_field_definition(_row(), public=True)
    assert "created_by" not in data
    assert "last_updated_by" not in data
    assert data["label"] == "Email"


def test_serialize_field_definition_authenticated_keeps_audit_fields():
    data = serialize_field_definition(_row(), public=False)
    assert data["created_by"] == "user-1"
    assert data["last_updated_by"] == "user-1"


def test_assert_public_readable_rejects_inactive():
    with pytest.raises(FieldDefinitionNotFoundError):
        assert_public_readable(_row(active=False))


def test_assert_public_readable_rejects_deleted():
    with pytest.raises(FieldDefinitionNotFoundError):
        assert_public_readable(_row(deleted=True))


def test_rate_limit_field_definitions_read_blocks_burst():
    request = MagicMock(spec=Request)
    request.headers = {}
    request.client = MagicMock()
    request.client.host = "test-rate-limit-client"

    bucket = "field-definitions:test-rate-limit-client"
    from api import field_definitions_public as mod

    mod._rate_buckets[bucket] = []

    for _ in range(mod._RATE_MAX_REQUESTS):
        rate_limit_field_definitions_read(request)

    with pytest.raises(HTTPException) as exc:
        rate_limit_field_definitions_read(request)
    assert exc.value.status_code == 429

    mod._rate_buckets[bucket] = []


def test_check_rate_limit_resets_after_window(monkeypatch):
    from api import field_definitions_public as mod

    bucket = "test-window"
    mod._rate_buckets[bucket] = []
    now = 1000.0
    monkeypatch.setattr(time, "monotonic", lambda: now)

    for _ in range(mod._RATE_MAX_REQUESTS):
        _check_rate_limit(bucket)

    with pytest.raises(HTTPException):
        _check_rate_limit(bucket)

    now += mod._RATE_WINDOW_SEC + 1
    _check_rate_limit(bucket)
    mod._rate_buckets[bucket] = []
