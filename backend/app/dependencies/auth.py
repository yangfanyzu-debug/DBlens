from fastapi import Depends, Header, HTTPException, Request

from app.config import settings
from app.schemas.auth import CurrentUser
from app.services.ruoyi_auth import RuoYiAuthError, fetch_current_user


def _is_local_dev_request(request: Request) -> bool:
    host = (request.headers.get("host") or "").split(":", 1)[0].lower()
    return settings.LOCAL_DEV_AUTH_ENABLED and host in {"127.0.0.1", "localhost"}


def _build_local_dev_user() -> CurrentUser:
    return CurrentUser(
        user_id=1,
        username="local-dev-admin",
        nickname="Local Dev",
        roles=["admin"],
        permissions=["*:*:*"],
        is_admin=True,
    )


async def get_current_user(request: Request, authorization: str | None = Header(default=None)):
    if not authorization:
        if _is_local_dev_request(request):
            return _build_local_dev_user()
        raise HTTPException(status_code=401, detail="RuoYi token missing")

    try:
        return await fetch_current_user(authorization)
    except RuoYiAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


async def require_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user
