import hmac
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from firebase_admin import auth as firebase_auth

from backend_api.api.deps import get_event_repository


class UserOrGuestListAuth:
    def __init__(self, user: "CurrentUser | None", is_guest_list: bool):
        self.user = user
        self.is_guest_list = is_guest_list


class CurrentUser:
    def __init__(self, uid: str, email: str | None = None, role: str = "user"):
        self.uid = uid
        self.email = email
        self.role = role


def _bearer_token(auth_header: str | None) -> str | None:
    if not auth_header or not auth_header.strip().lower().startswith("bearer "):
        return None
    return auth_header.strip()[7:].strip()


def get_current_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    token = _bearer_token(authorization or request.headers.get("authorization"))
    if not token:
        raise HTTPException(status_code=401, detail="No authorization header or token")
    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed") from e
    uid = decoded.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    return CurrentUser(
        uid=uid,
        email=decoded.get("email"),
        role=decoded.get("role", "user"),
    )


def require_roles(*allowed_roles: str):
    def _require(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _require


RequireAdmin = Depends(require_roles("admin"))
RequireOrganizer = Depends(require_roles("admin", "organizer"))


def get_optional_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser | None:
    token = _bearer_token(authorization or request.headers.get("authorization"))
    if not token:
        return None
    try:
        decoded = firebase_auth.verify_id_token(token)
        uid = decoded.get("uid")
        if not uid:
            return None
        return CurrentUser(
            uid=uid,
            email=decoded.get("email"),
            role=decoded.get("role", "user"),
        )
    except Exception:
        return None


def get_user_or_guest_list(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    x_guest_list_token: Annotated[str | None, Header(alias="X-Guest-List-Token")] = None,
    event_repo=Depends(get_event_repository),
) -> UserOrGuestListAuth:
    event_id = request.path_params.get("event_id") or request.path_params.get("id")
    if not event_id:
        raise HTTPException(status_code=401, detail="Missing event identifier")
    token = _bearer_token(authorization or request.headers.get("authorization"))
    if token:
        try:
            decoded = firebase_auth.verify_id_token(token)
            uid = decoded.get("uid")
            if uid:
                return UserOrGuestListAuth(
                    user=CurrentUser(
                        uid=uid,
                        email=decoded.get("email"),
                        role=decoded.get("role", "user"),
                    ),
                    is_guest_list=False,
                )
        except Exception:
            pass
    if x_guest_list_token is not None and x_guest_list_token != "":
        event = event_repo.get_by_id(event_id)
        if event and event.guest_list_token and hmac.compare_digest(event.guest_list_token, x_guest_list_token):
            return UserOrGuestListAuth(user=None, is_guest_list=True)
    raise HTTPException(status_code=401, detail="No authorization header or token")
