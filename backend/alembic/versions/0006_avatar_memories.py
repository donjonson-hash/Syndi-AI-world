"""SyndiAI D5 — avatar_memories table for three-layer memory.

UPGRADE:
  CREATE TABLE avatar_memories (if not exists) — долгосрочная память аватара:
    диалог, факты, контекст. Индексы на user_id и session_id.

DOWNGRADE:
  DROP TABLE avatar_memories.

Идемпотентна: проверяет существование таблицы и индексов перед созданием.

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    return inspect(bind).has_table(name)


def _index_exists(table: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    if not insp.has_table(table):
        return False
    for ix in insp.get_indexes(table):
        if ix.get("name") == index_name:
            return True
    return False


_INDEXES = [
    ("ix_avatar_mem_user",    "avatar_memories", ["user_id"]),
    ("ix_avatar_mem_session", "avatar_memories", ["session_id"]),
]


def upgrade() -> None:
    if not _table_exists("avatar_memories"):
        op.create_table(
            "avatar_memories",
            sa.Column("id",          sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id",     sa.Integer(),     nullable=False, index=True),
            sa.Column("session_id",  sa.String(),      nullable=False, index=True),
            sa.Column("memory_type", sa.String(20),    nullable=False),
            sa.Column("role",        sa.String(10),    nullable=False),
            sa.Column("content",     sa.Text(),        nullable=False),
            sa.Column("tags",        sa.Text(),        nullable=True),
            sa.Column("agent_mode",  sa.String(20),    nullable=True),
            sa.Column("mood",        sa.String(100),   nullable=True),
            sa.Column("created_at",  sa.DateTime(),    server_default=sa.func.now()),
        )

    for index_name, table, columns in _INDEXES:
        if not _table_exists(table):
            continue
        if _index_exists(table, index_name):
            continue
        try:
            op.create_index(index_name, table, columns)
        except Exception:
            pass


def downgrade() -> None:
    for index_name, table, _cols in _INDEXES:
        if not _table_exists(table):
            continue
        if not _index_exists(table, index_name):
            continue
        try:
            op.drop_index(index_name, table_name=table)
        except Exception:
            pass

    if _table_exists("avatar_memories"):
        try:
            op.drop_table("avatar_memories")
        except Exception:
            pass
