from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.operator import OperatorContext
from app.services import data_service, operation_logger
from app.services.connection_manager import ensure_engine

router = APIRouter(prefix="/api/data", tags=["data"])


def _db_type(conn_id: str) -> str:
    return ensure_engine(conn_id).dialect.name


class ChangeItem(BaseModel):
    op: str  # insert / update / delete
    pk_col: Optional[str] = None
    pk_val: Optional[str] = None
    values: Optional[dict] = None


class ChangesRequest(BaseModel):
    changes: list[ChangeItem]


@router.get("/{conn_id}/{database}/{table}")
async def get_table_data(
    conn_id: str, database: str, table: str,
    page: int = 1, page_size: int = 100,
    sort_col: Optional[str] = None, sort_dir: str = "ASC",
    filter_col: Optional[str] = None, filter_op: Optional[str] = None, filter_val: Optional[str] = None,
):
    try:
        db_type = _db_type(conn_id)
        return data_service.get_table_data(
            conn_id, db_type, database, table,
            page, page_size, sort_col, sort_dir,
            filter_col, filter_op, filter_val
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conn_id}/{database}/{table}/preview")
async def preview_changes(conn_id: str, database: str, table: str, req: ChangesRequest):
    try:
        db_type = _db_type(conn_id)
        sqls = data_service.preview_changes(conn_id, db_type, database, table, [c.model_dump() for c in req.changes])
        return {"changes": sqls}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{conn_id}/{database}/{table}/rows")
@router.put("/{conn_id}/{database}/{table}/rows")
@router.delete("/{conn_id}/{database}/{table}/rows")
async def apply_changes(
    conn_id: str,
    database: str,
    table: str,
    req: ChangesRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        db_type = _db_type(conn_id)
        data_service.apply_changes(conn_id, db_type, database, table, [c.model_dump() for c in req.changes])
        await operation_logger.record_operation(
            db,
            operator=OperatorContext.from_current_user(current_user),
            action="data.apply_changes",
            resource_type="table",
            conn_id=conn_id,
            db_name=database,
            table_name=table,
            detail={
                "change_count": len(req.changes),
                "ops": [change.op for change in req.changes],
            },
            status="success",
        )
        return {"ok": True}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conn_id}/{database}/{table}/export")
async def export_data(
    conn_id: str,
    database: str,
    table: str,
    format: str = "csv",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        db_type = _db_type(conn_id)
        content, media_type = data_service.export_data(conn_id, db_type, database, table, format)
        await operation_logger.record_operation(
            db,
            operator=OperatorContext.from_current_user(current_user),
            action="data.export",
            resource_type="table",
            conn_id=conn_id,
            db_name=database,
            table_name=table,
            detail={"format": format},
            status="success",
        )
        filename = f"{table}.{format}"
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
