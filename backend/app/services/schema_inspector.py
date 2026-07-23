from typing import Any
from sqlalchemy import text

from app.services.connection_manager import get_engine


def _exec(conn_id: str, sql: str, params: dict = None) -> list:
    engine = get_engine(conn_id)
    with engine.connect() as c:
        result = c.execute(text(sql), params or {})
        return result.fetchall()


def list_databases(conn_id: str, db_type: str) -> list[str]:
    if db_type == "mysql":
        rows = _exec(conn_id, "SHOW DATABASES")
        return [r[0] for r in rows]
    if db_type == "postgresql":
        rows = _exec(conn_id, "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
        return [r[0] for r in rows]
    if db_type == "sqlite":
        return ["main"]
    return []


def list_tables(conn_id: str, db_type: str, database: str) -> list[dict]:
    if db_type == "mysql":
        rows = _exec(conn_id,
            "SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = :db ORDER BY TABLE_NAME",
            {"db": database})
        return [{"name": r[0], "type": "VIEW" if r[1] == "VIEW" else "TABLE"} for r in rows]
    if db_type == "postgresql":
        rows = _exec(conn_id,
            "SELECT table_name, table_type FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name")
        return [{"name": r[0], "type": "VIEW" if r[1] == "VIEW" else "TABLE"} for r in rows]
    if db_type == "sqlite":
        rows = _exec(conn_id, "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")
        return [{"name": r[0], "type": r[1].upper()} for r in rows]
    return []


def list_columns(conn_id: str, db_type: str, database: str, table: str) -> list[dict]:
    if db_type == "mysql":
        rows = _exec(conn_id,
            "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT, "
            "COLUMN_KEY, EXTRA FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :tbl ORDER BY ORDINAL_POSITION",
            {"db": database, "tbl": table})
        return [{"name": r[0], "type": r[1], "nullable": r[2] == "YES",
                 "default": r[3], "comment": r[4],
                 "primary_key": r[5] == "PRI", "auto_increment": "auto_increment" in (r[6] or "")} for r in rows]
    if db_type == "postgresql":
        rows = _exec(conn_id,
            "SELECT column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name=:tbl ORDER BY ordinal_position",
            {"tbl": table})
        return [{"name": r[0], "type": r[1], "nullable": r[2] == "YES",
                 "default": r[3], "comment": None, "primary_key": False, "auto_increment": False} for r in rows]
    if db_type == "sqlite":
        rows = _exec(conn_id, f"PRAGMA table_info({table})")
        return [{"name": r[1], "type": r[2], "nullable": not r[3],
                 "default": r[4], "comment": None, "primary_key": bool(r[5]), "auto_increment": False} for r in rows]
    return []


def list_indexes(conn_id: str, db_type: str, database: str, table: str) -> list[dict]:
    if db_type == "mysql":
        rows = _exec(conn_id,
            "SELECT INDEX_NAME, NON_UNIQUE, COLUMN_NAME FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA=:db AND TABLE_NAME=:tbl ORDER BY INDEX_NAME, SEQ_IN_INDEX",
            {"db": database, "tbl": table})
        indexes: dict = {}
        for r in rows:
            name = r[0]
            if name not in indexes:
                indexes[name] = {"name": name, "type": "PRIMARY" if name == "PRIMARY" else ("INDEX" if r[1] else "UNIQUE"), "columns": []}
            indexes[name]["columns"].append(r[2])
        return list(indexes.values())
    if db_type == "postgresql":
        rows = _exec(conn_id,
            "SELECT i.relname, ix.indisunique, ix.indisprimary, a.attname "
            "FROM pg_class t JOIN pg_index ix ON t.oid=ix.indrelid "
            "JOIN pg_class i ON i.oid=ix.indexrelid "
            "JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=ANY(ix.indkey) "
            "WHERE t.relname=:tbl ORDER BY i.relname",
            {"tbl": table})
        indexes: dict = {}
        for r in rows:
            name = r[0]
            if name not in indexes:
                indexes[name] = {"name": name, "type": "PRIMARY" if r[2] else ("UNIQUE" if r[1] else "INDEX"), "columns": []}
            indexes[name]["columns"].append(r[3])
        return list(indexes.values())
    if db_type == "sqlite":
        rows = _exec(conn_id, f"PRAGMA index_list({table})")
        result = []
        for r in rows:
            cols = _exec(conn_id, f"PRAGMA index_info({r[1]})")
            result.append({"name": r[1], "type": "UNIQUE" if r[2] else "INDEX", "columns": [c[2] for c in cols]})
        return result
    return []


def list_foreign_keys(conn_id: str, db_type: str, database: str, table: str) -> list[dict]:
    if db_type == "mysql":
        rows = _exec(conn_id,
            "SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
            "FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA=:db AND TABLE_NAME=:tbl AND REFERENCED_TABLE_NAME IS NOT NULL",
            {"db": database, "tbl": table})
        return [{"name": r[0], "column": r[1], "ref_table": r[2], "ref_column": r[3]} for r in rows]
    if db_type == "postgresql":
        rows = _exec(conn_id,
            "SELECT tc.constraint_name, kcu.column_name, ccu.table_name, ccu.column_name "
            "FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name "
            "JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name "
            "WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_name=:tbl",
            {"tbl": table})
        return [{"name": r[0], "column": r[1], "ref_table": r[2], "ref_column": r[3]} for r in rows]
    if db_type == "sqlite":
        rows = _exec(conn_id, f"PRAGMA foreign_key_list({table})")
        return [{"name": f"fk_{r[0]}", "column": r[3], "ref_table": r[2], "ref_column": r[4]} for r in rows]
    return []


def get_table_ddl(conn_id: str, db_type: str, database: str, table: str) -> str:
    if db_type == "mysql":
        qualified_table = f"{_quote_identifier(database, '`')}.{_quote_identifier(table, '`')}"
        rows = _exec(conn_id, f"SHOW CREATE TABLE {qualified_table}")
        return _ensure_semicolon(rows[0][1]) if rows else ""

    if db_type == "sqlite":
        rows = _exec(
            conn_id,
            "SELECT sql FROM sqlite_master "
            "WHERE name=:tbl AND type IN ('table', 'view')",
            {"tbl": table},
        )
        return _ensure_semicolon(rows[0][0]) if rows and rows[0][0] else ""

    if db_type == "postgresql":
        return _build_postgresql_ddl(conn_id, table)

    return ""


def _build_postgresql_ddl(conn_id: str, table: str) -> str:
    qualified_name = f"public.{_quote_identifier(table, chr(34))}"
    columns = _exec(
        conn_id,
        "SELECT a.attname, pg_catalog.format_type(a.atttypid, a.atttypmod), "
        "a.attnotnull, pg_get_expr(ad.adbin, ad.adrelid) "
        "FROM pg_attribute a "
        "LEFT JOIN pg_attrdef ad ON ad.adrelid=a.attrelid AND ad.adnum=a.attnum "
        "WHERE a.attrelid=to_regclass(:qualified) AND a.attnum>0 AND NOT a.attisdropped "
        "ORDER BY a.attnum",
        {"qualified": qualified_name},
    )
    constraints = _exec(
        conn_id,
        "SELECT conname, pg_get_constraintdef(oid, true) "
        "FROM pg_constraint WHERE conrelid=to_regclass(:qualified) ORDER BY conname",
        {"qualified": qualified_name},
    )
    indexes = _exec(
        conn_id,
        "SELECT pg_get_indexdef(i.indexrelid) "
        "FROM pg_index i "
        "LEFT JOIN pg_constraint c ON c.conindid=i.indexrelid "
        "WHERE i.indrelid=to_regclass(:qualified) AND c.oid IS NULL "
        "ORDER BY i.indexrelid::regclass::text",
        {"qualified": qualified_name},
    )

    definitions = []
    for name, data_type, not_null, default in columns:
        column = f"{_quote_identifier(name, chr(34))} {data_type}"
        if default is not None:
            column += f" DEFAULT {default}"
        if not_null:
            column += " NOT NULL"
        definitions.append(f"  {column}")
    for name, definition in constraints:
        definitions.append(f"  CONSTRAINT {_quote_identifier(name, chr(34))} {definition}")

    table_name = f'{_quote_identifier("public", chr(34))}.{_quote_identifier(table, chr(34))}'
    ddl = f"CREATE TABLE {table_name} (\n" + ",\n".join(definitions) + "\n);"
    index_statements = [_ensure_semicolon(row[0]) for row in indexes if row[0]]
    return "\n\n".join([ddl, *index_statements])


def _quote_identifier(value: str, quote: str) -> str:
    return f"{quote}{value.replace(quote, quote * 2)}{quote}"


def _ensure_semicolon(statement: str) -> str:
    normalized = statement.rstrip()
    return normalized if normalized.endswith(";") else f"{normalized};"


def get_full_schema(conn_id: str, db_type: str, database: str) -> dict:
    tables = list_tables(conn_id, db_type, database)
    schema = {"tables": [t["name"] for t in tables], "columns": {}}
    for t in tables:
        schema["columns"][t["name"]] = list_columns(conn_id, db_type, database, t["name"])
    return schema
