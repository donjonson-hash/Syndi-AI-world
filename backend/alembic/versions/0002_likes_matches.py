"""SyndiAI v0.2 — likes + matches tables (Tinder механика)

Что делает эта миграция:
  UPGRADE:
    1. CREATE TABLE IF NOT EXISTS likes
    2. CREATE TABLE IF NOT EXISTS matches

  DOWNGRADE:
    1. DROP TABLE matches
    2. DROP TABLE likes

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    return inspect(bind).has_table(name)


def upgrade() -> None:
    # ── likes ─────────────────────────────────────────────────────────────
    if not _table_exists("likes"):
        op.create_table(
            "likes",
            sa.Column("id",           sa.String(36),  primary_key=True),
            sa.Column("from_user_id", sa.Integer(),   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("to_user_id",   sa.Integer(),   sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("is_like",      sa.Boolean(),   nullable=False),
            sa.Column("created_at",   sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_likes_from_to", "likes", ["from_user_id", "to_user_id"], unique=True)
        op.create_index("ix_likes_to_user", "likes", ["to_user_id"])

    # ── matches ───────────────────────────────────────────────────────────
    if not _table_exists("matches"):
        op.create_table(
            "matches",
            sa.Column("id",          sa.String(36), primary_key=True),
            sa.Column("user_a_id",   sa.Integer(),  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_b_id",   sa.Integer(),  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("match_score", sa.Float(),    nullable=True),
            sa.Column("status",      sa.String(20), nullable=False, server_default="active"),
            sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_matches_pair",   "matches", ["user_a_id", "user_b_id"], unique=True)
        op.create_index("ix_matches_user_a", "matches", ["user_a_id"])
        op.create_index("ix_matches_user_b", "matches", ["user_b_id"])
        op.create_index("ix_matches_status", "matches", ["status"])


def downgrade() -> None:
    if _table_exists("matches"):
        op.drop_index("ix_matches_status", table_name="matches")
        op.drop_index("ix_matches_user_b",  table_name="matches")
        op.drop_index("ix_matches_user_a",  table_name="matches")
        op.drop_index("ix_matches_pair",    table_name="matches")
        op.drop_table("matches")

    if _table_exists("likes"):
        op.drop_index("ix_likes_to_user", table_name="likes")
        op.drop_index("ix_likes_from_to", table_name="likes")
        op.drop_table("likes")
