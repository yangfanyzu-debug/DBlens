from dataclasses import dataclass

from app.schemas.auth import CurrentUser


@dataclass(frozen=True)
class OperatorContext:
    user_id: int
    username: str
    roles: tuple[str, ...]
    is_admin: bool

    @classmethod
    def from_current_user(cls, current_user: CurrentUser) -> "OperatorContext":
        return cls(
            user_id=current_user.user_id,
            username=current_user.username,
            roles=tuple(current_user.roles),
            is_admin=current_user.is_admin,
        )
