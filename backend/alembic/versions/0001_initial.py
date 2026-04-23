"""initial

Revision ID: 0001
Revises:
Create Date: 2026-04-23

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "connections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("db_type", sa.Enum("mysql", "postgresql", "sqlite"), nullable=False),
        sa.Column("host", sa.String(256)),
        sa.Column("port", sa.Integer()),
        sa.Column("username", sa.String(128)),
        sa.Column("password_enc", sa.Text()),
        sa.Column("database", sa.String(128)),
        sa.Column("group_name", sa.String(64)),
        sa.Column("ssh_enabled", sa.Boolean(), default=False),
        sa.Column("ssh_host", sa.String(256)),
        sa.Column("ssh_port", sa.Integer(), default=22),
        sa.Column("ssh_username", sa.String(128)),
        sa.Column("ssh_password_enc", sa.Text()),
        sa.Column("ssh_private_key", sa.Text()),
        sa.Column("ssl_enabled", sa.Boolean(), default=False),
        sa.Column("ssl_ca", sa.Text()),
        sa.Column("ssl_cert", sa.Text()),
        sa.Column("ssl_key", sa.Text()),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_table(
        "query_sessions",
        sa.Column("query_id", sa.String(36), primary_key=True),
        sa.Column("conn_id", sa.String(36), sa.ForeignKey("connections.id")),
        sa.Column("database", sa.String(128)),
        sa.Column("sql", sa.Text()),
        sa.Column("status", sa.Enum("running", "success", "error", "killed"), default="running"),
        sa.Column("db_thread_id", sa.Integer()),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("error_msg", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("query_sessions")
    op.drop_table("connections")
