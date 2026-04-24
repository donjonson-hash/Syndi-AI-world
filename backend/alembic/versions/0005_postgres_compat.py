"""SyndiAI D7 — PostgreSQL compatibility: ensure indexes on commonly queried columns.

UPGRADE:
  Создаёт индексы (если ещё не созданы) на колонках, которые часто
  участвуют в WHERE / JOIN:
    - founder_profiles.user_id   (JOIN users <-> founder_profiles)
    - likes.from_user_id         (выборка "кого я лайкнул")
    - likes.to_user_id           (выборка "кто меня лайкнул")
    - matches.user_a_id          (выборка матчей пользователя)
    - matches.user_b_id

DOWNGRADE:
  Удаляет индексы, добавленные в upgrade.

Все операции идемпотентны — проверяют существование индекса и таблицы
перед ALTER TABLE. Работает одинаково в SQLite и PostgreSQL.

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-24
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "0005"
down_revision: Union[str, None] = "0004"
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


# (index_name, table, [columns])
_INDEXES = [
    ("ix_d7_founder_profiles_user_id", "founder_profiles", ["user_id"]),
    ("ix_d7_likes_from_user_id",       "likes",            ["from_user_id"]),
    ("ix_d7_likes_to_user_id",         "likes",            ["to_user_id"]),
    ("ix_d7_matches_user_a_id",        "matches",          ["user_a_id"]),
    ("ix_d7_matches_user_b_id",        "matches",          ["user_b_id"]),
]


def upgrade() -> None:
    for index_name, table, columns in _INDEXES:
        if not _table_exists(table):
            continue
        if _index_exists(table, index_name):
            continue
        try:
            op.create_index(index_name, table, columns)
        except Exception:
            # индекс уже существует под другим именем или конфликт — пропускаем
            pass


def downgrade() -> None:
    for index_name, table, _columns in _INDEXES:
        if not _table_exists(table):
            continue
        if not _index_exists(table, index_name):
            continue
        try:
            op.drop_index(index_name, table_name=table)
        except Exception:
            pass
