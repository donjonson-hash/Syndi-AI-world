"""SyndiAI C4 — users.hashed_password column for JWT auth.

UPGRADE:
  1. ADD COLUMN users.hashed_password String(255) NULL — only if column missing.

DOWNGRADE:
  1. DROP COLUMN users.hashed_password — only if column present.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    return inspect(bind).has_table(name)


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    if not inspect(bind).has_table(table):
        return False
    cols = [c["name"] for c in inspect(bind).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if _table_exists("users") and not _column_exists("users", "hashed_password"):
        with op.batch_alter_table("users") as batch:
            batch.add_column(sa.Column("hashed_password", sa.String(255), nullable=True))


def downgrade() -> None:
    if _column_exists("users", "hashed_password"):
        with op.batch_alter_table("users") as batch:
            batch.drop_column("hashed_password")
