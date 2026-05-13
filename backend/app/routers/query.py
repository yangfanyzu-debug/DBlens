import asyncio
from uuid import uuid4
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.schemas.operator import OperatorContext
from app.schemas.query import QueryExecuteRequest
from app.services import operation_logger, query_executor
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("/execute", include_in_schema=True)
async def execute_query(
    req: QueryExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    query_id = req.query_id or str(uuid4())
    background_tasks.add_task(
        query_executor.execute_query,
        req.conn_id, req.database, req.sql, query_id, OperatorContext.from_current_user(current_user)
    )
    return {"query_id": query_id, "status": "running"}


@router.delete("/{query_id}")
async def kill_query(
    query_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await query_executor.kill_query(query_id)
    await operation_logger.record_operation(
        db,
        operator=OperatorContext.from_current_user(current_user),
        action="query.kill",
        resource_type="query",
        resource_id=query_id,
    )
    return {"ok": True}
