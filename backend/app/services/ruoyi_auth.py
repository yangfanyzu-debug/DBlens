import asyncio
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import settings
from app.schemas.auth import CurrentUser


class RuoYiAuthError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def map_ruoyi_user(payload: dict) -> CurrentUser:
    user = payload.get("user") or {}
    roles = list(payload.get("roles") or [])
    permissions = list(payload.get("permissions") or [])
    user_id = int(user["userId"])
    is_admin = "admin" in roles or user_id == 1
    return CurrentUser(
        user_id=user_id,
        username=user["userName"],
        nickname=user.get("nickName"),
        roles=roles,
        permissions=permissions,
        is_admin=is_admin,
    )


def _build_userinfo_url() -> str:
    return f"{settings.RUOYI_BASE_URL.rstrip('/')}/{settings.RUOYI_USERINFO_PATH.lstrip('/')}"


def _load_userinfo(authorization: str) -> dict:
    request = Request(
        _build_userinfo_url(),
        headers={
            settings.RUOYI_TOKEN_HEADER: authorization,
            "Accept": "application/json",
        },
        method="GET",
    )
    with urlopen(request, timeout=settings.RUOYI_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


async def fetch_current_user(authorization: str) -> CurrentUser:
    try:
        payload = await asyncio.to_thread(_load_userinfo, authorization)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise RuoYiAuthError(401, "RuoYi token invalid") from exc
        raise RuoYiAuthError(502, "RuoYi user info request failed") from exc
    except URLError as exc:
        raise RuoYiAuthError(502, "RuoYi user info request failed") from exc

    if payload.get("code") not in (None, 200):
        raise RuoYiAuthError(401, payload.get("msg") or "RuoYi token invalid")

    try:
        return map_ruoyi_user(payload)
    except (KeyError, TypeError, ValueError) as exc:
        raise RuoYiAuthError(502, "RuoYi user info payload invalid") from exc
