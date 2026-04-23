from pydantic import BaseModel
from typing import Optional


class ConnectionCreate(BaseModel):
    name: str
    db_type: str  # mysql / postgresql / sqlite
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None  # plaintext, will be encrypted
    database: Optional[str] = None
    group_name: Optional[str] = None

    ssh_enabled: bool = False
    ssh_host: Optional[str] = None
    ssh_port: int = 22
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_private_key: Optional[str] = None

    ssl_enabled: bool = False
    ssl_ca: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None


class ConnectionUpdate(ConnectionCreate):
    pass


class ConnectionOut(BaseModel):
    id: str
    name: str
    db_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    database: Optional[str] = None
    group_name: Optional[str] = None
    ssh_enabled: bool
    ssh_host: Optional[str] = None
    ssh_port: int
    ssh_username: Optional[str] = None
    ssl_enabled: bool

    model_config = {"from_attributes": True}


class TestResult(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[int] = None
