import asyncio
import time
import re
from datetime import datetime
from typing import Optional
from uuid import uuid4
from threading import Event, Lock
from contextlib import contextmanager
from dataclasses import dataclass, field

from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.schemas.operator import OperatorContext
from app.services import operation_logger
from app.services.connection_manager import ensure_engine
from app.ws.manager import ws_manager


@dataclass
class RunningQuery:
    engine: object
    thread_id: int
    lock: object = field(default_factory=Lock)
    active: bool = True
    discard_connection: bool = False


_running: dict[str, RunningQuery] = {}
_killed: set[str] = set()
ROW_LIMIT = 500
QUERY_TIMEOUT = 30


@contextmanager
def _query_connection(engine, query_id):
    with engine.connect() as conn:
        mysql_limit = None
        try:
            if engine.dialect.name == "mysql":
                mysql_limit = int(conn.execute(text("SELECT @@SESSION.sql_select_limit")).scalar())
                tid = int(conn.execute(text("SELECT CONNECTION_ID()")).scalar())
                _running[query_id] = RunningQuery(engine, tid)
            yield conn
        finally:
            state = _running.get(query_id)
            if state:
                # A checked-out connection cannot be reused while a cancel is sent.
                with state.lock:
                    state.active = False
                    _running.pop(query_id, None)
                    if state.discard_connection:
                        # Even an unacknowledged KILL must never target a reused connection.
                        conn.invalidate()
                        mysql_limit = None
            if mysql_limit is not None:
                try:
                    conn.execution_options(stream_results=False).execute(
                        text(f"SET SESSION sql_select_limit = {mysql_limit}")
                    )
                except Exception:
                    conn.invalidate()


def _split_statements(sql: str) -> list[str]:
    # Simple split on ; not inside quotes
    parts = re.split(r";(?=(?:[^'\"]*['\"][^'\"]*['\"])*[^'\"]*$)", sql)
    return [p.strip() for p in parts if p.strip()]


def _mysql_table_case_hint(engine, error_message: str) -> str | None:
    if getattr(engine.dialect, "name", None) != "mysql" or "1146" not in error_message:
        return None

    match = re.search(r"Table '([^']+)' doesn't exist", error_message)
    if not match or "." not in match.group(1):
        return None

    schema_name, requested_table = match.group(1).rsplit(".", 1)

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT TABLE_NAME FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA = :schema_name "
                    "AND LOWER(TABLE_NAME) = LOWER(:requested_table)"
                ),
                {"schema_name": schema_name, "requested_table": requested_table},
            ).fetchall()
    except Exception:
        return None

    matches = [row[0] for row in rows if row[0] != requested_table]
    if len(matches) != 1:
        return None

    actual_table = matches[0]
    return (
        "MySQL table names are case-sensitive on this server; "
        f"actual table name is `{actual_table}`. "
        f"Use `{actual_table}` instead of `{requested_table}`."
    )


def _format_query_error(engine, error: Exception) -> str:
    message = str(error)
    hint = _mysql_table_case_hint(engine, message)
    return f"{message}\nHint: {hint}" if hint else message


def _run_query_sync(conn_id: str, database: str, sql: str, query_id: str, expired=None):
    """Synchronous query runner — runs in thread pool to avoid blocking event loop."""
    engine = ensure_engine(conn_id)
    db_type = engine.dialect.name
    print(f"[QE] Got engine for {conn_id}, dialect={db_type}")

    statements = _split_statements(sql)
    results = []
    total_start = time.monotonic()
    expired = expired or Event()
    deadline = total_start + QUERY_TIMEOUT
    sqlite_raw = None

    def check_deadline():
        if query_id in _killed:
            raise RuntimeError("查询已终止")
        if expired.is_set() or time.monotonic() >= deadline:
            raise TimeoutError("查询超过 30 秒，已停止执行")

    try:
        with _query_connection(engine, query_id) as conn:
            check_deadline()
            if db_type == "sqlite":
                sqlite_raw = conn.connection.driver_connection
                sqlite_raw.set_progress_handler(lambda: int(expired.is_set() or time.monotonic() >= deadline), 1000)
            elif db_type == "postgresql":
                conn.execute(text("SET LOCAL statement_timeout = 30000"))
            if database and db_type == "mysql":
                conn.execute(text(f"USE `{database}`"))
            elif database and db_type == "postgresql":
                conn.execute(text(f"SET search_path TO {database}"))

            for stmt in statements:
                check_deadline()
                stmt_start = time.monotonic()
                # Server-side cursors avoid buffering the full result in the driver.
                leading_sql = re.sub(r"\A(?:\s|--[^\n]*(?:\n|$)|/\*.*?\*/)*", "", stmt, flags=re.S)
                reads_rows = bool(re.match(r"(?i)(SELECT|WITH)\b", leading_sql))
                if db_type == "mysql":
                    # MySQL applies this to SELECT without an explicit LIMIT.
                    conn.execution_options(stream_results=False).execute(
                        text(f"SET SESSION sql_select_limit = {ROW_LIMIT + 1}")
                    )
                if db_type == "postgresql":
                    conn.execution_options(stream_results=False).execute(text(f"SET LOCAL statement_timeout = {max(1, int((deadline - time.monotonic()) * 1000))}"))
                result = conn.execution_options(stream_results=db_type == "mysql" or (db_type == "postgresql" and reads_rows), max_row_buffer=ROW_LIMIT + 1).execute(text(stmt))
                elapsed = int((time.monotonic() - stmt_start) * 1000)

                stmt_type = stmt.strip().split()[0].upper() if stmt.strip() else "UNKNOWN"
                if result.returns_rows:
                    cols = list(result.keys())
                    fetched = result.fetchmany(ROW_LIMIT + 1)
                    rows = [list(r) for r in fetched[:ROW_LIMIT]]
                    results.append({
                        "sql": stmt, "type": stmt_type,
                        "columns": cols, "rows": rows,
                        "row_count": len(rows), "affected_rows": None,
                        "execution_ms": elapsed,
                        "truncated": len(fetched) > ROW_LIMIT,
                        "row_limit": ROW_LIMIT,
                    })
                else:
                    results.append({
                        "sql": stmt, "type": stmt_type,
                        "columns": [], "rows": [],
                        "row_count": 0, "affected_rows": result.rowcount,
                        "execution_ms": elapsed,
                    })
                result.close()
                check_deadline()
            if db_type == "sqlite":
                sqlite_raw.set_progress_handler(None, 0)
            conn.commit()

        total_ms = int((time.monotonic() - total_start) * 1000)
        return {
            "type": "result", "query_id": query_id,
            "status": "success", "statements": results,
            "total_ms": total_ms, "error": None,
        }
    except Exception as e:
        if query_id in _killed:
            return {
                "type": "result", "query_id": query_id,
                "status": "killed", "statements": results,
                "total_ms": int((time.monotonic() - total_start) * 1000),
                "error": None,
            }
        import traceback; traceback.print_exc()
        return {
            "type": "result", "query_id": query_id,
            "status": "error", "statements": results,
            "total_ms": int((time.monotonic() - total_start) * 1000),
            "error": _format_query_error(engine, e),
        }
    finally:
        if sqlite_raw is not None:
            sqlite_raw.set_progress_handler(None, 0)
        _running.pop(query_id, None)
        _killed.discard(query_id)


async def execute_query(
    conn_id: str,
    database: str,
    sql: str,
    query_id: str,
    operator: OperatorContext | None = None,
):
    print(f"[QE] Starting query {query_id} for conn {conn_id}")
    try:
        await ws_manager.send(query_id, {"type": "status", "query_id": query_id, "status": "running", "message": "Query started"})
    except Exception as e:
        print(f"[QE] Failed to send status: {e}")
        return

    try:
        expired = Event()
        work = asyncio.create_task(asyncio.to_thread(_run_query_sync, conn_id, database, sql, query_id, expired))
        try:
            result = await asyncio.wait_for(asyncio.shield(work), QUERY_TIMEOUT)
        except asyncio.TimeoutError:
            expired.set()
            running = _running.get(query_id)
            if running:
                try:
                    await _cancel_mysql(query_id, running)
                except Exception:
                    pass
            # Consume a late worker failure without publishing a second terminal result.
            work.add_done_callback(lambda task: task.exception() if not task.cancelled() else None)
            result = {"type": "result", "query_id": query_id, "status": "error", "statements": [], "total_ms": QUERY_TIMEOUT * 1000, "error": "查询超过 30 秒，已请求停止。请缩小查询范围后重试。"}
        print(f"[QE] Query done, sending result for {query_id}")
        await ws_manager.send(query_id, result)
        if operator:
            async with AsyncSessionLocal() as db:
                await operation_logger.record_operation(
                    db,
                    operator=operator,
                    action="query.execute",
                    resource_type="query",
                    resource_id=query_id,
                    conn_id=conn_id,
                    db_name=database,
                    sql_text=sql,
                    detail={"statement_count": len(_split_statements(sql))},
                    status=result["status"],
                    error_msg=result.get("error"),
                    duration_ms=result.get("total_ms"),
                )
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
    running = _running.get(query_id)
    if not running:
        await ws_manager.send(query_id, {
            "type": "result",
            "query_id": query_id,
            "status": "killed",
            "statements": [],
            "total_ms": 0,
            "error": None,
        })
        return

    await _cancel_mysql(query_id, running)

    await ws_manager.send(query_id, {
        "type": "result",
        "query_id": query_id,
        "status": "killed",
        "statements": [],
        "total_ms": 0,
        "error": None,
    })


async def _cancel_mysql(query_id, state):
    abandoned = Event()
    try:
        await asyncio.wait_for(asyncio.to_thread(_kill_mysql_query, query_id, state, abandoned), 2)
    finally:
        abandoned.set()


def _kill_mysql_query(query_id, state, abandoned):
    # Recreate retains the original connection creator (including TLS and SSH),
    # but has no checked-out business connections to wait for.
    pool = state.engine.pool.recreate()
    control = None
    try:
        control = pool.connect()
        control.driver_connection._read_timeout = 2
        control.driver_connection._write_timeout = 2
        with state.lock:
            if abandoned.is_set() or not state.active or _running.get(query_id) is not state:
                return
            cursor = control.cursor()
            try:
                state.discard_connection = True
                _killed.add(query_id)
                cursor.execute(f"KILL QUERY {state.thread_id}")
            finally:
                cursor.close()
    finally:
        try:
            if control is not None:
                control.close()
        finally:
            pool.dispose()
