import time
from typing import Dict, Tuple, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.models.connection import Connection
from app.schemas.operator import OperatorContext
from app.services import crypto


# { conn_id: (engine, tunnel_or_None) }
_pool: Dict[str, Tuple] = {}

# Synchronous engine for meta-DB (to reload connection config after restart)
_meta_engine = create_engine("sqlite:///./dblens_meta.db", pool_pre_ping=True)


def _build_url(conn: Connection, local_port: Optional[int] = None) -> str:
    host = "127.0.0.1" if local_port else conn.host
    port = local_port if local_port else conn.port

    if conn.db_type == "sqlite":
        return f"sqlite:///{conn.database}"

    password = crypto.decrypt(conn.password_enc) if conn.password_enc else ""
    if conn.db_type == "mysql":
        return f"mysql+pymysql://{conn.username}:{password}@{host}:{port}/{conn.database or ''}"
    if conn.db_type == "postgresql":
        return f"postgresql+psycopg2://{conn.username}:{password}@{host}:{port}/{conn.database or ''}"
    raise ValueError(f"Unsupported db_type: {conn.db_type}")


def _start_tunnel(conn: Connection):
    from sshtunnel import SSHTunnelForwarder
    ssh_password = crypto.decrypt(conn.ssh_password_enc) if conn.ssh_password_enc else None
    ssh_pkey = crypto.decrypt(conn.ssh_private_key) if conn.ssh_private_key else None

    tunnel = SSHTunnelForwarder(
        (conn.ssh_host, conn.ssh_port),
        ssh_username=conn.ssh_username,
        ssh_password=ssh_password,
        ssh_pkey=ssh_pkey,
        remote_bind_address=(conn.host, conn.port),
    )
    tunnel.start()
    return tunnel


def connect(conn: Connection):
    if conn.id in _pool:
        return

    tunnel = None
    local_port = None
    if conn.ssh_enabled:
        tunnel = _start_tunnel(conn)
        local_port = tunnel.local_bind_port

    url = _build_url(conn, local_port)
    connect_args = {}
    if conn.ssl_enabled and conn.db_type == "mysql":
        connect_args["ssl"] = {"ca": conn.ssl_ca, "cert": conn.ssl_cert, "key": conn.ssl_key}

    engine = create_engine(url, pool_size=5, max_overflow=10, connect_args=connect_args)
    _pool[conn.id] = (engine, tunnel)


def disconnect(conn_id: str):
    if conn_id not in _pool:
        return
    engine, tunnel = _pool.pop(conn_id)
    engine.dispose()
    if tunnel:
        tunnel.stop()


def get_engine(conn_id: str):
    if conn_id not in _pool:
        raise RuntimeError(f"Connection {conn_id} not open")
    return _pool[conn_id][0]


def ensure_engine(conn_id: str):
    """Get engine from pool, auto-reconnect if pool was cleared after restart."""
    try:
        return get_engine(conn_id)
    except RuntimeError:
        with Session(_meta_engine) as db:
            conn_obj = db.get(Connection, conn_id)
            if not conn_obj:
                raise RuntimeError(f"Connection {conn_id} not found in meta-DB")
            connect(conn_obj)
            return get_engine(conn_id)


def test_connection_from_form(
    data: dict,
    operator: OperatorContext | None = None,
) -> Tuple[bool, str, int]:
    """Test connection using raw form data (no DB save required)."""
    tunnel = None
    local_port = None
    try:
        db_type = data.get("db_type")
        host = data.get("host") or "127.0.0.1"
        port = data.get("port") or (3306 if db_type == "mysql" else 5432)
        username = data.get("username") or ""
        password = data.get("password") or ""
        database = data.get("database") or ""
        ssh_enabled = data.get("ssh_enabled", False)
        ssh_host = data.get("ssh_host") or ""
        ssh_port = data.get("ssh_port") or 22
        ssh_username = data.get("ssh_username") or ""
        ssh_password = data.get("ssh_password") or ""

        if ssh_enabled:
            tunnel = _start_tunnel_from_form(host, port, ssh_host, ssh_port, ssh_username, ssh_password, data.get("ssh_private_key"))
            local_port = tunnel.local_bind_port

        if db_type == "sqlite":
            url = f"sqlite:///{database}"
        elif db_type == "mysql":
            url = f"mysql+pymysql://{username}:{password}@{('127.0.0.1' if local_port else host)}:{local_port or port}/{database}"
        elif db_type == "postgresql":
            url = f"postgresql+psycopg2://{username}:{password}@{('127.0.0.1' if local_port else host)}:{local_port or port}/{database}"
        else:
            return False, f"Unsupported db_type: {db_type}", 0

        engine = create_engine(url, pool_pre_ping=True)
        start = time.monotonic()
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        latency = int((time.monotonic() - start) * 1000)
        engine.dispose()
        return True, f"Connected in {latency}ms", latency
    except Exception as e:
        return False, str(e), 0
    finally:
        if tunnel:
            tunnel.stop()


def _start_tunnel_from_form(target_host: str, target_port: int, ssh_host: str, ssh_port: int, ssh_username: str, ssh_password: str, ssh_private_key: str | None):
    from sshtunnel import SSHTunnelForwarder
    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        ssh_pkey=ssh_private_key,
        remote_bind_address=(target_host, target_port),
    )
    tunnel.start()
    return tunnel


def test_connection(
    conn: Connection,
    operator: OperatorContext | None = None,
) -> Tuple[bool, str, int]:
    tunnel = None
    local_port = None
    try:
        if conn.ssh_enabled:
            tunnel = _start_tunnel(conn)
            local_port = tunnel.local_bind_port

        url = _build_url(conn, local_port)
        engine = create_engine(url, pool_pre_ping=True)
        start = time.monotonic()
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        latency = int((time.monotonic() - start) * 1000)
        engine.dispose()
        return True, f"Connected in {latency}ms", latency
    except Exception as e:
        return False, str(e), 0
    finally:
        if tunnel:
            tunnel.stop()
