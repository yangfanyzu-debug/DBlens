from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    db_type: Mapped[str] = mapped_column(Enum("mysql", "postgresql", "sqlite", "doris"), nullable=False)
    host: Mapped[str | None] = mapped_column(String(256))
    port: Mapped[int | None] = mapped_column(Integer)
    username: Mapped[str | None] = mapped_column(String(128))
    password_enc: Mapped[str | None] = mapped_column(Text)
    database: Mapped[str | None] = mapped_column(String(128))
    group_name: Mapped[str | None] = mapped_column(String(64))

    ssh_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    ssh_host: Mapped[str | None] = mapped_column(String(256))
    ssh_port: Mapped[int] = mapped_column(Integer, default=22)
    ssh_username: Mapped[str | None] = mapped_column(String(128))
    ssh_password_enc: Mapped[str | None] = mapped_column(Text)
    ssh_private_key: Mapped[str | None] = mapped_column(Text)

    ssl_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    ssl_ca: Mapped[str | None] = mapped_column(Text)
    ssl_cert: Mapped[str | None] = mapped_column(Text)
    ssl_key: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
