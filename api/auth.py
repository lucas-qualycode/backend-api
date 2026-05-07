from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from firebase_admin import auth as firebase_auth


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
        # TODO: Uncomment this when we have a way to set roles
        # if current_user.role not in allowed_roles:
        #     raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _require


RequireAdmin = Depends(require_roles("admin"))
RequireOrganizer = Depends(require_roles("admin", "organizer"))
