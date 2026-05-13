import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation_log import OperationLog
from app.schemas.operator import OperatorContext

MAX_SQL_TEXT_LENGTH = 4000


def _truncate(value: str | None, max_length: int) -> str | None:
    if value is None:
        return None
    return value[:max_length]


def _serialize_detail(detail: dict[str, Any] | None) -> str | None:
    if detail is None:
        return None
    return json.dumps(detail, ensure_ascii=False, default=str)


async def record_operation(
    db: AsyncSession,
    *,
    operator: OperatorContext,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    conn_id: str | None = None,
    db_name: str | None = None,
    table_name: str | None = None,
    sql_text: str | None = None,
    detail: dict[str, Any] | None = None,
    status: str = "success",
    error_msg: str | None = None,
    duration_ms: int | None = None,
) -> bool:
    try:
        db.add(
            OperationLog(
                user_id=operator.user_id,
                username=operator.username,
                roles=",".join(operator.roles),
                is_admin=operator.is_admin,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                conn_id=conn_id,
                db_name=db_name,
                table_name=table_name,
                sql_text=_truncate(sql_text, MAX_SQL_TEXT_LENGTH),
                detail=_serialize_detail(detail),
                status=status,
                error_msg=_truncate(error_msg, MAX_SQL_TEXT_LENGTH),
                duration_ms=duration_ms,
            )
        )
        await db.commit()
        return True
    except Exception:
        rollback = getattr(db, "rollback", None)
        if rollback:
            await rollback()
        return False
