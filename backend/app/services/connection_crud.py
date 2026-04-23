import time
from uuid import uuid4
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.connection import Connection
from app.schemas.connection import ConnectionCreate, ConnectionUpdate
from app.services import crypto


async def list_connections(db: AsyncSession):
    result = await db.execute(select(Connection))
    return result.scalars().all()


async def get_connection(db: AsyncSession, conn_id: str) -> Optional[Connection]:
    result = await db.execute(select(Connection).where(Connection.id == conn_id))
    return result.scalar_one_or_none()


async def create_connection(db: AsyncSession, data: ConnectionCreate) -> Connection:
    conn = Connection(
        id=str(uuid4()),
        name=data.name,
        db_type=data.db_type,
        host=data.host,
        port=data.port,
        username=data.username,
        password_enc=crypto.encrypt(data.password) if data.password else None,
        database=data.database,
        group_name=data.group_name,
        ssh_enabled=data.ssh_enabled,
        ssh_host=data.ssh_host,
        ssh_port=data.ssh_port,
        ssh_username=data.ssh_username,
        ssh_password_enc=crypto.encrypt(data.ssh_password) if data.ssh_password else None,
        ssh_private_key=crypto.encrypt(data.ssh_private_key) if data.ssh_private_key else None,
        ssl_enabled=data.ssl_enabled,
        ssl_ca=data.ssl_ca,
        ssl_cert=data.ssl_cert,
        ssl_key=data.ssl_key,
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)
    return conn


async def update_connection(db: AsyncSession, conn_id: str, data: ConnectionUpdate) -> Optional[Connection]:
    conn = await get_connection(db, conn_id)
    if not conn:
        return None
    conn.name = data.name
    conn.db_type = data.db_type
    conn.host = data.host
    conn.port = data.port
    conn.username = data.username
    if data.password is not None:
        conn.password_enc = crypto.encrypt(data.password)
    conn.database = data.database
    conn.group_name = data.group_name
    conn.ssh_enabled = data.ssh_enabled
    conn.ssh_host = data.ssh_host
    conn.ssh_port = data.ssh_port
    conn.ssh_username = data.ssh_username
    if data.ssh_password is not None:
        conn.ssh_password_enc = crypto.encrypt(data.ssh_password)
    if data.ssh_private_key is not None:
        conn.ssh_private_key = crypto.encrypt(data.ssh_private_key)
    conn.ssl_enabled = data.ssl_enabled
    conn.ssl_ca = data.ssl_ca
    conn.ssl_cert = data.ssl_cert
    conn.ssl_key = data.ssl_key
    await db.commit()
    await db.refresh(conn)
    return conn


async def delete_connection(db: AsyncSession, conn_id: str) -> bool:
    conn = await get_connection(db, conn_id)
    if not conn:
        return False
    await db.delete(conn)
    await db.commit()
    return True
