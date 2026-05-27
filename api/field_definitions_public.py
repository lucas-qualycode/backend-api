import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request

from api.auth import CurrentUser
from domain.field_definitions.entity import FieldDefinition, FieldDefinitionQueryParams
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError

PUBLIC_LIST_QUERY = FieldDefinitionQueryParams(active=True, deleted=False)

_RATE_WINDOW_SEC = 60
_RATE_MAX_REQUESTS = 120
_rate_buckets: dict[str, list[float]] = defaultdict(list)
_rate_lock = Lock()


def resolve_list_query_params(
    user: CurrentUser | None,
    *,
    active: bool | None,
    deleted: bool | None,
    field_type: str | None,
    limit: int | None,
    offset: int | None,
) -> tuple[FieldDefinitionQueryParams, bool]:
    if user is not None:
        return (
            FieldDefinitionQueryParams(
                active=active,
                deleted=deleted,
                field_type=field_type,
                limit=limit,
                offset=offset,
            ),
            False,
        )

    if active is not None and active is not True:
        raise HTTPException(
            status_code=400,
            detail="Public field definitions require active=true",
        )
    if deleted is not None and deleted is not False:
        raise HTTPException(
            status_code=400,
            detail="Public field definitions require deleted=false",
        )
    if field_type is not None:
        raise HTTPException(
            status_code=400,
            detail="field_type filter is not available for public field definition reads",
        )
    if limit is not None or offset is not None:
        raise HTTPException(
            status_code=400,
            detail="Pagination is not available for public field definition reads",
        )

    return PUBLIC_LIST_QUERY, True


def assert_public_readable(row: FieldDefinition) -> None:
    if not row.active or row.deleted:
        raise FieldDefinitionNotFoundError(row.id)


def serialize_field_definition(row: FieldDefinition, *, public: bool) -> dict:
    data = row.model_dump(mode="json")
    if public:
        data.pop("created_by", None)
        data.pop("last_updated_by", None)
    return data


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _check_rate_limit(bucket_key: str) -> None:
    now = time.monotonic()
    with _rate_lock:
        hits = _rate_buckets[bucket_key]
        cutoff = now - _RATE_WINDOW_SEC
        hits = [t for t in hits if t > cutoff]
        if len(hits) >= _RATE_MAX_REQUESTS:
            raise HTTPException(status_code=429, detail="Too many requests")
        hits.append(now)
        _rate_buckets[bucket_key] = hits


def rate_limit_field_definitions_read(request: Request) -> None:
    _check_rate_limit(f"field-definitions:{_client_key(request)}")
