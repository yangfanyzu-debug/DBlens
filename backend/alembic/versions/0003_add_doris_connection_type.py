"""add doris connection type

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-08

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            "ALTER TABLE connections MODIFY COLUMN db_type "
            "ENUM('mysql','postgresql','sqlite','doris') NOT NULL"
        )
    elif dialect == "postgresql":
        op.execute("ALTER TYPE db_type ADD VALUE IF NOT EXISTS 'doris'")


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            "ALTER TABLE connections MODIFY COLUMN db_type "
            "ENUM('mysql','postgresql','sqlite') NOT NULL"
        )
