from fastapi import APIRouter, HTTPException
from app.services import schema_inspector, connection_manager
from app.services.connection_manager import ensure_engine

router = APIRouter(prefix="/api/databases", tags=["databases"])


def _require_engine(conn_id: str):
    try:
        return ensure_engine(conn_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _get_db_type(conn_id: str) -> str:
    engine = _require_engine(conn_id)
    return engine.dialect.name  # "mysql", "postgresql", "sqlite"


@router.get("")
async def list_databases(conn_id: str):
    db_type = _get_db_type(conn_id)
    return schema_inspector.list_databases(conn_id, db_type)


@router.get("/{database}/tables")
async def list_tables(database: str, conn_id: str):
    db_type = _get_db_type(conn_id)
    return schema_inspector.list_tables(conn_id, db_type, database)


@router.get("/{database}/tables/{table}/columns")
async def list_columns(database: str, table: str, conn_id: str):
    db_type = _get_db_type(conn_id)
    return schema_inspector.list_columns(conn_id, db_type, database, table)


@router.get("/{database}/tables/{table}/indexes")
async def list_indexes(database: str, table: str, conn_id: str):
    db_type = _get_db_type(conn_id)
    return schema_inspector.list_indexes(conn_id, db_type, database, table)


@router.get("/{database}/tables/{table}/foreign_keys")
async def list_foreign_keys(database: str, table: str, conn_id: str):
    db_type = _get_db_type(conn_id)
    return schema_inspector.list_foreign_keys(conn_id, db_type, database, table)


@router.get("/{database}/schema")
async def get_schema(database: str, conn_id: str):
    db_type = _get_db_type(conn_id)
    return schema_inspector.get_full_schema(conn_id, db_type, database)
