"""SyndiAI v0.1 — founder profiles, matches, trials, events

Что делает эта миграция:
  UPGRADE:
    1. ALTER TABLE users — добавить email, is_active, created_at, updated_at
       (все nullable, существующие строки не трогаем)
    2. CREATE TABLE founder_profiles
    3. CREATE TABLE match_candidates
    4. CREATE TABLE trials
    5. CREATE TABLE trial_tasks
    6. CREATE TABLE trial_events

  DOWNGRADE (откат без потери users-данных):
    1. DROP TABLE trial_events, trial_tasks, trials, match_candidates, founder_profiles
    2. ALTER TABLE users — удалить новые колонки

Revision ID: 0001
Revises: —
Create Date: 2026-04-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ─── helpers ─────────────────────────────────────────────────────────────────

def _json():
    """JSON-совместимый тип: JSONB в Postgres, Text в SQLite."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        from sqlalchemy.dialects.postgresql import JSONB
        return JSONB
    return sa.Text


# ─── upgrade ─────────────────────────────────────────────────────────────────

def upgrade() -> None:
    J = _json()

    # ── 1. Расширяем таблицу users ────────────────────────────────────────
    # render_as_batch=True в env.py позволяет ALTER TABLE в SQLite
    with op.batch_alter_table("users", schema=None) as batch_op:
        # Проверяем через try/except — безопасно если колонка уже есть
        try:
            batch_op.add_column(sa.Column(
                "email", sa.String(255), nullable=True
            ))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column(
                "is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")
            ))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column(
                "created_at", sa.DateTime(timezone=True), nullable=True
            ))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column(
                "updated_at", sa.DateTime(timezone=True), nullable=True
            ))
        except Exception:
            pass

    # ── 2. founder_profiles ───────────────────────────────────────────────
    op.create_table(
        "founder_profiles",
        sa.Column("id",      sa.String(36), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("raw_answers",              J(), nullable=False),
        sa.Column("normalized_profile",       J(), nullable=False),
        sa.Column("onboarding_schema_version",
                  sa.String(64),
                  nullable=False,
                  server_default="syndiai-onboarding-schema-v0.1"),
        sa.Column("is_active",  sa.Boolean(),            nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_founder_profiles_user_id", "founder_profiles", ["user_id"])

    # ── 3. match_candidates ───────────────────────────────────────────────
    op.create_table(
        "match_candidates",
        sa.Column("id",                        sa.String(36), primary_key=True),
        sa.Column("requester_user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score_breakdown",           J(),         nullable=False),
        sa.Column("total_compatibility_score", sa.Float(), nullable=False),
        sa.Column("founder_fit_score",         sa.Float(), nullable=False),
        sa.Column("big5_fit_score",            sa.Float(), nullable=True),
        sa.Column("risk_flags",                J(),         nullable=False, server_default="[]"),
        sa.Column("scoring_model_version",     sa.String(64), nullable=False,
                  server_default="syndiai-founder-v0.1"),
        sa.Column("status",     sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("requester_user_id != candidate_user_id", name="ck_no_self_match"),
    )
    op.create_index("ix_match_candidates_requester", "match_candidates", ["requester_user_id"])
    op.create_index("ix_match_candidates_candidate", "match_candidates", ["candidate_user_id"])
    op.create_index("ix_match_candidates_score",     "match_candidates", ["total_compatibility_score"])
    op.create_index("ix_match_candidates_status",    "match_candidates", ["status"])

    # ── 4. trials ─────────────────────────────────────────────────────────
    op.create_table(
        "trials",
        sa.Column("id",       sa.String(36), primary_key=True),
        sa.Column("match_id", sa.String(36),
                  sa.ForeignKey("match_candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("initiator_id",   sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("participant_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scenario_type", sa.String(64), nullable=False, server_default="standard_3day"),
        sa.Column("duration_days", sa.Integer(),  nullable=False, server_default="3"),
        sa.Column("status",        sa.String(20), nullable=False, server_default="active"),
        sa.Column("started_at",    sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("ends_at",       sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at",  sa.DateTime(timezone=True), nullable=True),
        sa.Column("behavioral_summary", J(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_trials_match_id", "trials", ["match_id"])
    op.create_index("ix_trials_status",   "trials", ["status"])

    # ── 5. trial_tasks ────────────────────────────────────────────────────
    op.create_table(
        "trial_tasks",
        sa.Column("id",          sa.String(36), primary_key=True),
        sa.Column("trial_id",    sa.String(36),
                  sa.ForeignKey("trials.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title",       sa.String(255), nullable=False),
        sa.Column("description", sa.Text(),      nullable=True),
        sa.Column("due_at",      sa.DateTime(timezone=True), nullable=True),
        sa.Column("status",      sa.String(20),  nullable=False, server_default="pending"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at",   sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_trial_tasks_trial_id",    "trial_tasks", ["trial_id"])
    op.create_index("ix_trial_tasks_assigned_to", "trial_tasks", ["assigned_to"])

    # ── 6. trial_events ───────────────────────────────────────────────────
    op.create_table(
        "trial_events",
        sa.Column("id",         sa.String(36), primary_key=True),
        sa.Column("trial_id",   sa.String(36),
                  sa.ForeignKey("trials.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id",    sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload",    J(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_trial_events_trial_id",    "trial_events", ["trial_id"])
    op.create_index("ix_trial_events_user_id",     "trial_events", ["user_id"])
    op.create_index("ix_trial_events_type",        "trial_events", ["event_type"])
    op.create_index("ix_trial_events_occurred_at", "trial_events", ["occurred_at"])


# ─── downgrade ────────────────────────────────────────────────────────────────
# Откат удаляет только новые таблицы и новые колонки users.
# Существующие строки users сохраняются полностью.

def downgrade() -> None:
    # Удаляем новые таблицы в обратном порядке (зависимости)
    for tbl in ("trial_events", "trial_tasks", "trials",
                "match_candidates", "founder_profiles"):
        op.drop_table(tbl)

    # Удаляем новые колонки из users
    with op.batch_alter_table("users", schema=None) as batch_op:
        for col in ("updated_at", "created_at", "is_active", "email"):
            try:
                batch_op.drop_column(col)
            except Exception:
                pass
