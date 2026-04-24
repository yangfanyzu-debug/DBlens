from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import CurrentUser, CurrentUserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUserResponse)
async def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
):
    return CurrentUserResponse(user=current_user)
