"""
SyndiAI Database Models
Версия: syndiai-schema-v0.2

Принцип миграции без потери данных:
  - Таблица users расширяется новыми nullable-колонками (raw_answers, normalized_profile,
    onboarding_schema_version). Существующие строки сохраняются.
  - Новые таблицы (founder_profiles, match_candidates, trials, trial_tasks, trial_events)
    добавляются рядом.
  - v0.2: добавлены таблицы likes и matches для Tinder-механики.

SQLite: все типы совместимы (JSON → Text, UUID → String).
PostgreSQL: использует нативные JSONB для колонок с JSON (автоматически при использовании JSON типа).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Index, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship
from database.database import Base

def _now():
    return datetime.now(timezone.utc)

def _uuid():
    return str(uuid.uuid4())

# ─────────────────────────────────────────────────────────────────────────────
# Существующая таблица — users
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)

    skills            = Column(JSON, nullable=True)
    psycho_profile    = Column(JSON, nullable=True)
    enneagram         = Column(JSON, nullable=True)
    match_score       = Column(Float,    nullable=True)
    ai_interpretation = Column(Text,     nullable=True)

    email      = Column(String(255), unique=True, nullable=True)
    is_active  = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=True)

    founder_profile  = relationship("FounderProfileDB", back_populates="user",
                                    uselist=False, cascade="all, delete-orphan")
    initiated_trials = relationship("TrialDB", foreign_keys="TrialDB.initiator_id",
                                    back_populates="initiator")
    likes_given    = relationship("LikeDB", foreign_keys="LikeDB.from_user_id",
                                  back_populates="from_user", cascade="all, delete-orphan")
    likes_received = relationship("LikeDB", foreign_keys="LikeDB.to_user_id",
                                  back_populates="to_user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role}')>"

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "role": self.role,
            "skills": self.skills, "psycho_profile": self.psycho_profile,
            "enneagram": self.enneagram,
        }

# ─────────────────────────────────────────────────────────────────────────────
# founder_profiles
# ─────────────────────────────────────────────────────────────────────────────
class FounderProfileDB(Base):
    __tablename__ = "founder_profiles"

    id      = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, unique=True)

    raw_answers             = Column(JSON, nullable=False)
    normalized_profile      = Column(JSON, nullable=False)
    onboarding_schema_version = Column(String(64),
                                       default="syndiai-onboarding-schema-v0.1",
                                       nullable=False)

    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="founder_profile")
    match_requests  = relationship(
        "MatchCandidateDB",
        foreign_keys="MatchCandidateDB.requester_user_id",
        back_populates="requester_profile",
        primaryjoin="FounderProfileDB.user_id == MatchCandidateDB.requester_user_id"
    )

    __table_args__ = (
        Index("ix_founder_profiles_user_id", "user_id"),
    )

# ─────────────────────────────────────────────────────────────────────────────
# match_candidates
# ─────────────────────────────────────────────────────────────────────────────
class MatchCandidateDB(Base):
    __tablename__ = "match_candidates"

    id                 = Column(String(36), primary_key=True, default=_uuid)
    requester_user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    score_breakdown           = Column(JSON, nullable=False)
    total_compatibility_score = Column(Float,    nullable=False)
    founder_fit_score         = Column(Float,    nullable=False)
    big5_fit_score            = Column(Float,    nullable=True)
    risk_flags                = Column(JSON, nullable=False, default=list)
    scoring_model_version     = Column(String(64),
                                       default="syndiai-founder-v0.1", nullable=False)

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
# trials
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
    status             = Column(String(20),  default="active",        nullable=False)

    started_at         = Column(DateTime(timezone=True), default=_now,  nullable=False)
    ends_at            = Column(DateTime(timezone=True), nullable=False)
    completed_at       = Column(DateTime(timezone=True), nullable=True)
    behavioral_summary = Column(JSON, nullable=True)

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
# trial_tasks
# ─────────────────────────────────────────────────────────────────────────────
class TrialTaskDB(Base):
    __tablename__ = "trial_tasks"

    id          = Column(String(36), primary_key=True, default=_uuid)
    trial_id    = Column(String(36), ForeignKey("trials.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)

    title       = Column(String(255), nullable=False)
    description = Column(Text,        nullable=True)
    due_at      = Column(DateTime(timezone=True), nullable=True)
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
# trial_events
# ─────────────────────────────────────────────────────────────────────────────
class TrialEventDB(Base):
    __tablename__ = "trial_events"

    id         = Column(String(36), primary_key=True, default=_uuid)
    trial_id   = Column(String(36), ForeignKey("trials.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(Integer,    ForeignKey("users.id"),                       nullable=False)

    event_type  = Column(String(64), nullable=False)
    payload     = Column(JSON,   nullable=True)
    occurred_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    created_at  = Column(DateTime(timezone=True), default=_now, nullable=False)

    trial = relationship("TrialDB", back_populates="events")

    __table_args__ = (
        Index("ix_trial_events_trial_id",    "trial_id"),
        Index("ix_trial_events_user_id",     "user_id"),
        Index("ix_trial_events_type",        "event_type"),
        Index("ix_trial_events_occurred_at", "occurred_at"),
    )

# ─────────────────────────────────────────────────────────────────────────────
# likes — свайп-решение основателя (like / dislike)  [v0.2]
# ─────────────────────────────────────────────────────────────────────────────
class LikeDB(Base):
    __tablename__ = "likes"

    id           = Column(String(36), primary_key=True, default=_uuid)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_like      = Column(Boolean, nullable=False)   # True = like, False = dislike

    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="likes_given")
    to_user   = relationship("User", foreign_keys=[to_user_id],   back_populates="likes_received")

    __table_args__ = (
        Index("ix_likes_from_to", "from_user_id", "to_user_id", unique=True),
        Index("ix_likes_to_user", "to_user_id"),
    )

# ─────────────────────────────────────────────────────────────────────────────
# matches — взаимный лайк = match  [v0.2]
# ─────────────────────────────────────────────────────────────────────────────
class MatchDB(Base):
    __tablename__ = "matches"

    id        = Column(String(36), primary_key=True, default=_uuid)
    user_a_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    match_score = Column(Float, nullable=True)
    status      = Column(String(20), default="active", nullable=False)  # active / archived

    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    user_a = relationship("User", foreign_keys=[user_a_id])
    user_b = relationship("User", foreign_keys=[user_b_id])

    __table_args__ = (
        Index("ix_matches_pair",   "user_a_id", "user_b_id", unique=True),
        Index("ix_matches_user_a", "user_a_id"),
        Index("ix_matches_user_b", "user_b_id"),
        Index("ix_matches_status", "status"),
    )
