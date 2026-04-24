import asyncio
import time
import re
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import text

from app.services.connection_manager import ensure_engine
from app.ws.manager import ws_manager


# { query_id: db_thread_id } for kill support
_running: dict[str, int] = {}


def _split_statements(sql: str) -> list[str]:
    # Simple split on ; not inside quotes
    parts = re.split(r";(?=(?:[^'\"]*['\"][^'\"]*['\"])*[^'\"]*$)", sql)
    return [p.strip() for p in parts if p.strip()]


def _run_query_sync(conn_id: str, database: str, sql: str, query_id: str):
    """Synchronous query runner — runs in thread pool to avoid blocking event loop."""
    engine = ensure_engine(conn_id)
    db_type = engine.dialect.name
    print(f"[QE] Got engine for {conn_id}, dialect={db_type}")

    statements = _split_statements(sql)
    results = []
    total_start = time.monotonic()

    try:
        with engine.connect() as conn:
            if database and db_type == "mysql":
                conn.execute(text(f"USE `{database}`"))
            elif database and db_type == "postgresql":
                conn.execute(text(f"SET search_path TO {database}"))

            if db_type == "mysql":
                tid = conn.execute(text("SELECT CONNECTION_ID()")).scalar()
                _running[query_id] = tid

            for stmt in statements:
                stmt_start = time.monotonic()
                result = conn.execute(text(stmt))
                elapsed = int((time.monotonic() - stmt_start) * 1000)

                stmt_type = stmt.strip().split()[0].upper() if stmt.strip() else "UNKNOWN"
                if result.returns_rows:
                    cols = list(result.keys())
                    rows = [list(r) for r in result.fetchall()]
                    results.append({
                        "sql": stmt, "type": stmt_type,
                        "columns": cols, "rows": rows,
                        "row_count": len(rows), "affected_rows": None,
                        "execution_ms": elapsed,
                    })
                else:
                    results.append({
                        "sql": stmt, "type": stmt_type,
                        "columns": [], "rows": [],
                        "row_count": 0, "affected_rows": result.rowcount,
                        "execution_ms": elapsed,
                    })
            conn.commit()

        total_ms = int((time.monotonic() - total_start) * 1000)
        return {
            "type": "result", "query_id": query_id,
            "status": "success", "statements": results,
            "total_ms": total_ms, "error": None,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        return {
            "type": "result", "query_id": query_id,
            "status": "error", "statements": results,
            "total_ms": int((time.monotonic() - total_start) * 1000),
            "error": str(e),
        }
    finally:
        _running.pop(query_id, None)


async def execute_query(conn_id: str, database: str, sql: str, query_id: str):
    print(f"[QE] Starting query {query_id} for conn {conn_id}")
    try:
        await ws_manager.send(query_id, {"type": "status", "query_id": query_id, "status": "running", "message": "Query started"})
    except Exception as e:
        print(f"[QE] Failed to send status: {e}")
        return

    try:
        result = await asyncio.to_thread(_run_query_sync, conn_id, database, sql, query_id)
        print(f"[QE] Query done, sending result for {query_id}")
        await ws_manager.send(query_id, result)
    except Exception as e:
        print(f"[QE] Outer error: {e}")
        import traceback; traceback.print_exc()
        try:
            await ws_manager.send(query_id, {
                "type": "result", "query_id": query_id, "status": "error",
                "statements": [], "total_ms": 0, "error": f"Unexpected error: {e}",
            })
        except:
            pass


async def kill_query(query_id: str):
    thread_id = _running.get(query_id)
    if not thread_id:
        return
    _running.pop(query_id, None)
    await ws_manager.send(query_id, {
        "type": "result",
        "query_id": query_id,
        "status": "killed",
        "statements": [],
        "total_ms": 0,
        "error": None,
    })
