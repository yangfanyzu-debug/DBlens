from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: int
    username: str
    nickname: str | None = None
    roles: list[str]
    permissions: list[str]
    is_admin: bool


class CurrentUserResponse(BaseModel):
    user: CurrentUser
