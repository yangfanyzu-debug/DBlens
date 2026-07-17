import csv
import io
import json
from typing import Optional, Any
from sqlalchemy import text

from app.services.connection_manager import get_engine


def _use_db(conn, db_type: str, database: str):
    if database and db_type == "mysql":
        conn.execute(text(f"USE `{database}`"))
    elif database and db_type == "postgresql":
        conn.execute(text(f"SET search_path TO {database}"))


def get_table_data(conn_id: str, db_type: str, database: str, table: str,
                   page: int, page_size: int,
                   sort_col: Optional[str], sort_dir: str,
                   filter_col: Optional[str], filter_op: Optional[str], filter_val: Optional[str]) -> dict:
    engine = get_engine(conn_id)
    with engine.connect() as conn:
        _use_db(conn, db_type, database)

        where = ""
        params: dict = {}
        if filter_col and filter_op and filter_val is not None:
            if filter_op == "eq":
                where = f"WHERE `{filter_col}` = :fval" if db_type == "mysql" else f'WHERE "{filter_col}" = :fval'
            elif filter_op == "like":
                where = f"WHERE `{filter_col}` LIKE :fval" if db_type == "mysql" else f'WHERE "{filter_col}" LIKE :fval'
                filter_val = f"%{filter_val}%"
            elif filter_op == "gt":
                where = f"WHERE `{filter_col}` > :fval" if db_type == "mysql" else f'WHERE "{filter_col}" > :fval'
            elif filter_op == "lt":
                where = f"WHERE `{filter_col}` < :fval" if db_type == "mysql" else f'WHERE "{filter_col}" < :fval'
            params["fval"] = filter_val

        order = ""
        if sort_col:
            direction = "DESC" if sort_dir.upper() == "DESC" else "ASC"
            order = f"ORDER BY `{sort_col}` {direction}" if db_type == "mysql" else f'ORDER BY "{sort_col}" {direction}'

        tbl = f"`{table}`" if db_type == "mysql" else f'"{table}"'
        count_row = conn.execute(text(f"SELECT COUNT(*) FROM {tbl} {where}"), params).scalar()
        offset = (page - 1) * page_size
        rows_result = conn.execute(
            text(f"SELECT * FROM {tbl} {where} {order} LIMIT :lim OFFSET :off"),
            {**params, "lim": page_size, "off": offset}
        )
        columns = [{"name": c, "type": ""} for c in rows_result.keys()]
        rows = [list(r) for r in rows_result.fetchall()]

    return {"columns": columns, "rows": rows, "total": count_row, "page": page, "page_size": page_size}


def preview_changes(conn_id: str, db_type: str, database: str, table: str, changes: list[dict]) -> list[dict]:
    sqls = []
    tbl = f"`{table}`" if db_type == "mysql" else f'"{table}"'
    for change in changes:
        op = change.get("op")
        if op == "update":
            pk_col = change["pk_col"]
            pk_val = change["pk_val"]
            updates = ", ".join(
                f"`{k}` = {_preview_value(v)}" if db_type == "mysql" else f'"{k}" = {_preview_value(v)}'
                for k, v in change["values"].items()
            )
            pk_expr = f"`{pk_col}`" if db_type == "mysql" else f'"{pk_col}"'
            sqls.append({"type": "UPDATE", "sql": f"UPDATE {tbl} SET {updates} WHERE {pk_expr} = {_preview_value(pk_val)}"})
        elif op == "insert":
            if not change["values"]:
                continue
            cols = ", ".join(f"`{k}`" if db_type == "mysql" else f'"{k}"' for k in change["values"])
            vals = ", ".join(_preview_value(v) for v in change["values"].values())
            sqls.append({"type": "INSERT", "sql": f"INSERT INTO {tbl} ({cols}) VALUES ({vals})"})
        elif op == "delete":
            pk_col = change["pk_col"]
            pk_val = change["pk_val"]
            pk_expr = f"`{pk_col}`" if db_type == "mysql" else f'"{pk_col}"'
            sqls.append({"type": "DELETE", "sql": f"DELETE FROM {tbl} WHERE {pk_expr} = {_preview_value(pk_val)}"})
    return sqls


def apply_changes(conn_id: str, db_type: str, database: str, table: str, changes: list[dict]):
    engine = get_engine(conn_id)
    with engine.begin() as conn:
        _use_db(conn, db_type, database)
        for statement, params in _build_change_statements(db_type, table, changes):
            conn.execute(text(statement), params)


def _preview_value(value: Any) -> str:
    if value is None:
        return "NULL"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _quote_identifier(db_type: str, name: str) -> str:
    return f"`{name}`" if db_type == "mysql" else f'"{name}"'


def _build_change_statements(db_type: str, table: str, changes: list[dict]) -> list[tuple[str, dict]]:
    statements = []
    tbl = _quote_identifier(db_type, table)
    for idx, change in enumerate(changes):
        op = change.get("op")
        values = change.get("values") or {}
        if op == "update":
            assignments = []
            params = {"pk": change["pk_val"]}
            for value_idx, (key, value) in enumerate(values.items()):
                param_name = f"v_{idx}_{value_idx}"
                assignments.append(f"{_quote_identifier(db_type, key)} = :{param_name}")
                params[param_name] = value
            if not assignments:
                continue
            pk_col = _quote_identifier(db_type, change["pk_col"])
            statements.append((f"UPDATE {tbl} SET {', '.join(assignments)} WHERE {pk_col} = :pk", params))
        elif op == "insert":
            if not values:
                continue
            cols = []
            placeholders = []
            params = {}
            for value_idx, (key, value) in enumerate(values.items()):
                param_name = f"v_{idx}_{value_idx}"
                cols.append(_quote_identifier(db_type, key))
                placeholders.append(f":{param_name}")
                params[param_name] = value
            statements.append((f"INSERT INTO {tbl} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})", params))
        elif op == "delete":
            pk_col = _quote_identifier(db_type, change["pk_col"])
            statements.append((f"DELETE FROM {tbl} WHERE {pk_col} = :pk", {"pk": change["pk_val"]}))
    return statements


def export_data(conn_id: str, db_type: str, database: str, table: str, fmt: str,
                columns: Optional[list[str]] = None) -> tuple[str, str]:
    engine = get_engine(conn_id)
    with engine.connect() as conn:
        _use_db(conn, db_type, database)
        tbl = f"`{table}`" if db_type == "mysql" else f'"{table}"'
        col_expr = "*"
        if columns:
            col_expr = ", ".join(f"`{c}`" if db_type == "mysql" else f'"{c}"' for c in columns)
        result = conn.execute(text(f"SELECT {col_expr} FROM {tbl}"))
        keys = list(result.keys())
        rows = [list(r) for r in result.fetchall()]

    if fmt == "json":
        data = json.dumps([dict(zip(keys, r)) for r in rows], default=str, ensure_ascii=False)
        return data, "application/json"

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(keys)
    writer.writerows(rows)
    return buf.getvalue(), "text/csv"
