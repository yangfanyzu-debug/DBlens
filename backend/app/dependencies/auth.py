from fastapi import Depends, Header, HTTPException

from app.services.ruoyi_auth import RuoYiAuthError, fetch_current_user


async def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="RuoYi token missing")

    try:
        return await fetch_current_user(authorization)
    except RuoYiAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


async def require_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user
