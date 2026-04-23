from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.services import data_service
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
async def apply_changes(conn_id: str, database: str, table: str, req: ChangesRequest):
    try:
        db_type = _db_type(conn_id)
        data_service.apply_changes(conn_id, db_type, database, table, [c.model_dump() for c in req.changes])
        return {"ok": True}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conn_id}/{database}/{table}/export")
async def export_data(conn_id: str, database: str, table: str, format: str = "csv"):
    try:
        db_type = _db_type(conn_id)
        content, media_type = data_service.export_data(conn_id, db_type, database, table, format)
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
