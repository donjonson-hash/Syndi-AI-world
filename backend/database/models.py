"""
SyndiAI Database Models
Версия: syndiai-schema-v0.1

Принцип миграции без потери данных:
  - Таблица users расширяется новыми nullable-колонками (raw_answers, normalized_profile,
    onboarding_schema_version). Существующие строки сохраняются.
  - Новые таблицы (founder_profiles, match_candidates, trials, trial_tasks, trial_events)
    добавляются рядом.

SQLite: все типы совместимы (JSON → Text, UUID → String, ARRAY → JSON).
PostgreSQL: используй нативные типы через conditional import ниже.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Index, Integer, String, Text,
)
from sqlalchemy.orm import relationship
from database.database import Base

# JSON / ARRAY-совместимый тип (SQLite хранит как Text, Postgres — как JSONB)
try:
    from sqlalchemy.dialects.postgresql import JSONB as JSONType, ARRAY
    _pg = True
except ImportError:
    from sqlalchemy import JSON as JSONType
    _pg = False


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# Существующая таблица — users
# Расширена nullable-колонками для SyndiAI v0.1.
# Старые строки не затрагиваются.
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    # ── Старые поля (неизменны) ────────────────────────────────────────────
    id   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)

    skills            = Column(JSONType, nullable=True)
    psycho_profile    = Column(JSONType, nullable=True)
    enneagram         = Column(JSONType, nullable=True)
    match_score       = Column(Float,    nullable=True)
    ai_interpretation = Column(Text,     nullable=True)

    # ── Новые поля SyndiAI v0.1 (все nullable → нет проблем с существующими строками) ─
    email      = Column(String(255), unique=True, nullable=True)
    is_active  = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=True)

    # ── Отношения ──────────────────────────────────────────────────────────
    founder_profile  = relationship("FounderProfileDB", back_populates="user",
                                    uselist=False, cascade="all, delete-orphan")
    initiated_trials = relationship("TrialDB", foreign_keys="TrialDB.initiator_id",
                                    back_populates="initiator")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role}')>"

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "role": self.role,
            "skills": self.skills, "psycho_profile": self.psycho_profile,
            "enneagram": self.enneagram,
        }


# ─────────────────────────────────────────────────────────────────────────────
# founder_profiles — хранит raw + normalized profile основателя
# ─────────────────────────────────────────────────────────────────────────────
class FounderProfileDB(Base):
    __tablename__ = "founder_profiles"

    id      = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, unique=True)

    raw_answers             = Column(JSONType, nullable=False)
    normalized_profile      = Column(JSONType, nullable=False)
    onboarding_schema_version = Column(String(64),
                                       default="syndiai-onboarding-schema-v0.1",
                                       nullable=False)

    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="founder_profile")
    match_requests  = relationship("MatchCandidateDB",
                                   foreign_keys="MatchCandidateDB.requester_user_id",
                                   back_populates="requester_profile")

    __table_args__ = (
        Index("ix_founder_profiles_user_id", "user_id"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# match_candidates — результат score_pair() для пары основателей
# ─────────────────────────────────────────────────────────────────────────────
class MatchCandidateDB(Base):
    __tablename__ = "match_candidates"

    id                 = Column(String(36), primary_key=True, default=_uuid)
    requester_user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    score_breakdown           = Column(JSONType, nullable=False)
    total_compatibility_score = Column(Float,    nullable=False)
    founder_fit_score         = Column(Float,    nullable=False)
    big5_fit_score            = Column(Float,    nullable=True)
    # SQLite-friendly: храним как JSON-список строк
    risk_flags                = Column(JSONType, nullable=False, default=list)
    scoring_model_version     = Column(String(64),
                                       default="syndiai-founder-v0.1", nullable=False)

    # Статус: pending | accepted | declined | expired
    status     = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    requester_profile = relationship(
        "FounderProfileDB",
        foreign_keys=[requester_user_id],
        back_populates="match_requests",
        primaryjoin="MatchCandidateDB.requester_user_id == FounderProfileDB.user_id",
    )

    __table_args__ = (
        Index("ix_match_candidates_requester", "requester_user_id"),
        Index("ix_match_candidates_candidate", "candidate_user_id"),
        Index("ix_match_candidates_score",     "total_compatibility_score"),
        Index("ix_match_candidates_status",    "status"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# trials — 3–5-дневный поведенческий тест
# ─────────────────────────────────────────────────────────────────────────────
class TrialDB(Base):
    __tablename__ = "trials"

    id             = Column(String(36), primary_key=True, default=_uuid)
    match_id       = Column(String(36), ForeignKey("match_candidates.id", ondelete="CASCADE"),
                            nullable=False)
    initiator_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    scenario_type      = Column(String(64),  default="standard_3day", nullable=False)
    duration_days      = Column(Integer,     default=3,               nullable=False)
    # Статус: active | completed | abandoned | expired
    status             = Column(String(20),  default="active",        nullable=False)

    started_at         = Column(DateTime(timezone=True), default=_now,  nullable=False)
    ends_at            = Column(DateTime(timezone=True), nullable=False)
    completed_at       = Column(DateTime(timezone=True), nullable=True)
    behavioral_summary = Column(JSONType, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    initiator = relationship("User", foreign_keys=[initiator_id],
                             back_populates="initiated_trials")
    tasks  = relationship("TrialTaskDB",  back_populates="trial",
                          cascade="all, delete-orphan")
    events = relationship("TrialEventDB", back_populates="trial",
                          cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_trials_match_id", "match_id"),
        Index("ix_trials_status",   "status"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# trial_tasks — задачи внутри trial
# ─────────────────────────────────────────────────────────────────────────────
class TrialTaskDB(Base):
    __tablename__ = "trial_tasks"

    id          = Column(String(36), primary_key=True, default=_uuid)
    trial_id    = Column(String(36), ForeignKey("trials.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)

    title       = Column(String(255), nullable=False)
    description = Column(Text,        nullable=True)
    due_at      = Column(DateTime(timezone=True), nullable=True)
    # Статус: pending | in_progress | completed | missed
    status      = Column(String(20), default="pending", nullable=False)

    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at   = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at   = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    trial = relationship("TrialDB", back_populates="tasks")

    __table_args__ = (
        Index("ix_trial_tasks_trial_id",    "trial_id"),
        Index("ix_trial_tasks_assigned_to", "assigned_to"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# trial_events — behavioral telemetry
# ─────────────────────────────────────────────────────────────────────────────
class TrialEventDB(Base):
    __tablename__ = "trial_events"

    id         = Column(String(36), primary_key=True, default=_uuid)
    trial_id   = Column(String(36), ForeignKey("trials.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(Integer,    ForeignKey("users.id"),                       nullable=False)

    # task_completed | message_sent | deadline_missed | check_in |
    # review_submitted | trial_abandoned | custom
    event_type  = Column(String(64), nullable=False)
    payload     = Column(JSONType,   nullable=True)
    occurred_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    created_at  = Column(DateTime(timezone=True), default=_now, nullable=False)

    trial = relationship("TrialDB", back_populates="events")

    __table_args__ = (
        Index("ix_trial_events_trial_id",    "trial_id"),
        Index("ix_trial_events_user_id",     "user_id"),
        Index("ix_trial_events_type",        "event_type"),
        Index("ix_trial_events_occurred_at", "occurred_at"),
    )
