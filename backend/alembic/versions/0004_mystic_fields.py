"""SyndiAI C8 — mystic fields on founder_profiles (MBTI + enneagram).

UPGRADE:
  1. ADD COLUMN founder_profiles.mbti_type       VARCHAR(4) NULL — if missing.
  2. ADD COLUMN founder_profiles.enneagram_type  INTEGER    NULL — if missing.

DOWNGRADE:
  1. DROP COLUMN founder_profiles.enneagram_type — if present.
  2. DROP COLUMN founder_profiles.mbti_type      — if present.

Все операции идемпотентны — опираются на `_column_exists()` / `_table_exists()`.

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0004"
down_revision: Union[str, None] = "0003"
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
    if not _table_exists("founder_profiles"):
        return
    with op.batch_alter_table("founder_profiles") as batch:
        if not _column_exists("founder_profiles", "mbti_type"):
            batch.add_column(sa.Column("mbti_type", sa.String(4), nullable=True))
        if not _column_exists("founder_profiles", "enneagram_type"):
            batch.add_column(sa.Column("enneagram_type", sa.Integer(), nullable=True))


def downgrade() -> None:
    if not _table_exists("founder_profiles"):
        return
    with op.batch_alter_table("founder_profiles") as batch:
        if _column_exists("founder_profiles", "enneagram_type"):
            batch.drop_column("enneagram_type")
        if _column_exists("founder_profiles", "mbti_type"):
            batch.drop_column("mbti_type")
