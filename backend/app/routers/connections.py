from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_admin_user
from app.database import get_db
from app.schemas.connection import ConnectionCreate, ConnectionUpdate, ConnectionOut, TestResult
from app.schemas.operator import OperatorContext
from app.services import connection_crud, connection_manager, operation_logger

router = APIRouter(prefix="/api/connections", tags=["connections"])


def _connection_log_detail(conn) -> dict:
    return {
        "name": getattr(conn, "name", None),
        "db_type": getattr(conn, "db_type", None),
    }


@router.get("", response_model=list[ConnectionOut])
async def list_connections(
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    return await connection_crud.list_connections(db)


@router.post("", response_model=ConnectionOut)
async def create_connection(
    data: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_user),
):
    operator = OperatorContext.from_current_user(current_user)
    conn = await connection_crud.create_connection(
        db,
        data,
        operator=operator,
    )
    await operation_logger.record_operation(
        db,
        operator=operator,
        action="connection.create",
        resource_type="connection",
        resource_id=getattr(conn, "id", None),
        conn_id=getattr(conn, "id", None),
        db_name=getattr(conn, "database", None),
        detail=_connection_log_detail(conn),
    )
    return conn


@router.post("/test-form", response_model=TestResult)
async def test_connection_form(
    data: ConnectionCreate,
    current_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Test a connection using form data before saving."""
    operator = OperatorContext.from_current_user(current_user)
    success, message, latency = connection_manager.test_connection_from_form(
        data.model_dump(),
        operator=operator,
    )
    await operation_logger.record_operation(
        db,
        operator=operator,
        action="connection.test_form",
        resource_type="connection",
        db_name=data.database,
        detail={"name": data.name, "db_type": data.db_type, "success": success},
        status="success" if success else "error",
        error_msg=None if success else message,
        duration_ms=latency,
    )
    return TestResult(success=success, message=message, latency_ms=latency)


@router.get("/{conn_id}", response_model=ConnectionOut)
async def get_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    conn = await connection_crud.get_connection(db, conn_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn


@router.put("/{conn_id}", response_model=ConnectionOut)
async def update_connection(
    conn_id: str,
    data: ConnectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_user),
):
    operator = OperatorContext.from_current_user(current_user)
    conn = await connection_crud.update_connection(
        db,
        conn_id,
        data,
        operator=operator,
    )
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    await operation_logger.record_operation(
        db,
        operator=operator,
        action="connection.update",
        resource_type="connection",
        resource_id=getattr(conn, "id", conn_id),
        conn_id=getattr(conn, "id", conn_id),
        db_name=getattr(conn, "database", None),
        detail=_connection_log_detail(conn),
    )
    return conn


@router.delete("/{conn_id}")
async def delete_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_user),
):
    operator = OperatorContext.from_current_user(current_user)
    ok = await connection_crud.delete_connection(
        db,
        conn_id,
        operator=operator,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Connection not found")
    connection_manager.disconnect(conn_id)
    await operation_logger.record_operation(
        db,
        operator=operator,
        action="connection.delete",
        resource_type="connection",
        resource_id=conn_id,
        conn_id=conn_id,
    )
    return {"ok": True}


@router.post("/{conn_id}/test", response_model=TestResult)
async def test_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin_user),
):
    conn = await connection_crud.get_connection(db, conn_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    operator = OperatorContext.from_current_user(current_user)
    success, message, latency = connection_manager.test_connection(
        conn,
        operator=operator,
    )
    await operation_logger.record_operation(
        db,
        operator=operator,
        action="connection.test",
        resource_type="connection",
        resource_id=getattr(conn, "id", conn_id),
        conn_id=getattr(conn, "id", conn_id),
        db_name=getattr(conn, "database", None),
        detail={**_connection_log_detail(conn), "success": success},
        status="success" if success else "error",
        error_msg=None if success else message,
        duration_ms=latency,
    )
    return TestResult(success=success, message=message, latency_ms=latency)


@router.post("/{conn_id}/connect")
async def open_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conn = await connection_crud.get_connection(db, conn_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    connection_manager.connect(conn)
    await operation_logger.record_operation(
        db,
        operator=OperatorContext.from_current_user(current_user),
        action="connection.connect",
        resource_type="connection",
        resource_id=getattr(conn, "id", conn_id),
        conn_id=getattr(conn, "id", conn_id),
        db_name=getattr(conn, "database", None),
        detail=_connection_log_detail(conn),
    )
    return {"ok": True}


@router.delete("/{conn_id}/disconnect")
async def close_connection(
    conn_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    connection_manager.disconnect(conn_id)
    await operation_logger.record_operation(
        db,
        operator=OperatorContext.from_current_user(current_user),
        action="connection.disconnect",
        resource_type="connection",
        resource_id=conn_id,
        conn_id=conn_id,
    )
    return {"ok": True}
