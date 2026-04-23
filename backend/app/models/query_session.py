from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class QuerySession(Base):
    __tablename__ = "query_sessions"

    query_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conn_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("connections.id"))
    database: Mapped[str | None] = mapped_column(String(128))
    sql: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Enum("running", "success", "error", "killed"), default="running")
    db_thread_id: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_msg: Mapped[str | None] = mapped_column(Text)
