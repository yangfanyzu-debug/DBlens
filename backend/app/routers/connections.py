from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.connection import ConnectionCreate, ConnectionUpdate, ConnectionOut, TestResult
from app.services import connection_crud, connection_manager

router = APIRouter(prefix="/api/connections", tags=["connections"])


@router.get("", response_model=list[ConnectionOut])
async def list_connections(db: AsyncSession = Depends(get_db)):
    return await connection_crud.list_connections(db)


@router.post("", response_model=ConnectionOut)
async def create_connection(data: ConnectionCreate, db: AsyncSession = Depends(get_db)):
    return await connection_crud.create_connection(db, data)


@router.post("/test-form", response_model=TestResult)
async def test_connection_form(data: ConnectionCreate):
    """Test a connection using form data before saving."""
    success, message, latency = connection_manager.test_connection_from_form(data.model_dump())
    return TestResult(success=success, message=message, latency_ms=latency)


@router.get("/{conn_id}", response_model=ConnectionOut)
async def get_connection(conn_id: str, db: AsyncSession = Depends(get_db)):
    conn = await connection_crud.get_connection(db, conn_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn


@router.put("/{conn_id}", response_model=ConnectionOut)
async def update_connection(conn_id: str, data: ConnectionUpdate, db: AsyncSession = Depends(get_db)):
    conn = await connection_crud.update_connection(db, conn_id, data)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn


@router.delete("/{conn_id}")
async def delete_connection(conn_id: str, db: AsyncSession = Depends(get_db)):
    ok = await connection_crud.delete_connection(db, conn_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Connection not found")
    connection_manager.disconnect(conn_id)
    return {"ok": True}


@router.post("/{conn_id}/test", response_model=TestResult)
async def test_connection(conn_id: str, db: AsyncSession = Depends(get_db)):
    conn = await connection_crud.get_connection(db, conn_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    success, message, latency = connection_manager.test_connection(conn)
    return TestResult(success=success, message=message, latency_ms=latency)


@router.post("/{conn_id}/connect")
async def open_connection(conn_id: str, db: AsyncSession = Depends(get_db)):
    conn = await connection_crud.get_connection(db, conn_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    connection_manager.connect(conn)
    return {"ok": True}


@router.delete("/{conn_id}/disconnect")
async def close_connection(conn_id: str):
    connection_manager.disconnect(conn_id)
    return {"ok": True}
