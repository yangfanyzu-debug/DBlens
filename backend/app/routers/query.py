import asyncio
from uuid import uuid4
from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.schemas.query import QueryExecuteRequest
from app.services import query_executor

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("/execute", include_in_schema=True)
async def execute_query(req: QueryExecuteRequest, background_tasks: BackgroundTasks):
    query_id = req.query_id or str(uuid4())
    background_tasks.add_task(
        query_executor.execute_query,
        req.conn_id, req.database, req.sql, query_id
    )
    return {"query_id": query_id, "status": "running"}


@router.delete("/{query_id}")
async def kill_query(query_id: str):
    await query_executor.kill_query(query_id)
    return {"ok": True}
