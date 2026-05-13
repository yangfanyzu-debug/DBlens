"""add operation logs

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operation_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.Integer()),
        sa.Column("username", sa.String(128)),
        sa.Column("roles", sa.String(512)),
        sa.Column("is_admin", sa.Boolean(), default=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.String(128)),
        sa.Column("conn_id", sa.String(36)),
        sa.Column("db_name", sa.String(128)),
        sa.Column("table_name", sa.String(128)),
        sa.Column("sql_text", sa.Text()),
        sa.Column("detail", sa.Text()),
        sa.Column("status", sa.String(16), nullable=False, default="success"),
        sa.Column("error_msg", sa.Text()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("ix_operation_logs_created_at", "operation_logs", ["created_at"])
    op.create_index("ix_operation_logs_user_id", "operation_logs", ["user_id"])
    op.create_index("ix_operation_logs_action", "operation_logs", ["action"])


def downgrade() -> None:
    op.drop_index("ix_operation_logs_action", table_name="operation_logs")
    op.drop_index("ix_operation_logs_user_id", table_name="operation_logs")
    op.drop_index("ix_operation_logs_created_at", table_name="operation_logs")
    op.drop_table("operation_logs")
