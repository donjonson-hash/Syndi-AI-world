-- SyndiAI Founder Matching — PostgreSQL Schema v0.1
-- Поддерживает: анкета → профиль → матч → trial → behavioral telemetry

-- ─────────────────────────────────────────────
-- Extensions
-- ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────
-- Users
-- ─────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─────────────────────────────────────────────
-- Founder Profiles
-- Хранит и raw answers, и normalized_profile
-- ─────────────────────────────────────────────
CREATE TABLE founder_profiles (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Raw ответы онбординга (JSON)
    raw_answers             JSONB NOT NULL,

    -- Нормализованный профиль (JSON, структура FounderProfile)
    normalized_profile      JSONB NOT NULL,

    -- Версия схемы онбординга (для миграций)
    onboarding_schema_version TEXT NOT NULL DEFAULT 'syndiai-onboarding-schema-v0.1',

    is_active               BOOLEAN NOT NULL DEFAULT true,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT one_active_profile_per_user UNIQUE (user_id)
);

CREATE INDEX idx_founder_profiles_user_id ON founder_profiles(user_id);

-- ─────────────────────────────────────────────
-- Match Candidates
-- Результаты pair scoring между двумя профилями
-- ─────────────────────────────────────────────
CREATE TABLE match_candidates (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_user_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    candidate_user_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Полный ScoreBreakdown (JSON)
    score_breakdown          JSONB NOT NULL,

    -- Основные метрики для быстрых запросов
    total_compatibility_score FLOAT NOT NULL,
    founder_fit_score         FLOAT NOT NULL,
    big5_fit_score            FLOAT,
    risk_flags                TEXT[] NOT NULL DEFAULT '{}',

    -- Версия модели скоринга
    scoring_model_version     TEXT NOT NULL DEFAULT 'syndiai-founder-v0.1',

    -- Статус: pending | accepted | declined | expired
    status                    TEXT NOT NULL DEFAULT 'pending',

    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT no_self_match CHECK (requester_user_id != candidate_user_id)
);

CREATE INDEX idx_match_candidates_requester ON match_candidates(requester_user_id);
CREATE INDEX idx_match_candidates_candidate ON match_candidates(candidate_user_id);
CREATE INDEX idx_match_candidates_score ON match_candidates(total_compatibility_score DESC);
CREATE INDEX idx_match_candidates_status ON match_candidates(status);

-- ─────────────────────────────────────────────
-- Trials
-- 3–5-дневный поведенческий тест после матча
-- ─────────────────────────────────────────────
CREATE TABLE trials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id        UUID NOT NULL REFERENCES match_candidates(id) ON DELETE CASCADE,
    initiator_id    UUID NOT NULL REFERENCES users(id),
    participant_id  UUID NOT NULL REFERENCES users(id),

    scenario_type   TEXT NOT NULL DEFAULT 'standard_3day',
    duration_days   INT  NOT NULL DEFAULT 3,

    -- Статус: active | completed | abandoned | expired
    status          TEXT NOT NULL DEFAULT 'active',

    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    ends_at         TIMESTAMPTZ NOT NULL,
    completed_at    TIMESTAMPTZ,

    -- Агрегированные поведенческие метрики
    behavioral_summary JSONB,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_trials_match_id ON trials(match_id);
CREATE INDEX idx_trials_status ON trials(status);

-- ─────────────────────────────────────────────
-- Trial Tasks
-- Задачи внутри trial-периода
-- ─────────────────────────────────────────────
CREATE TABLE trial_tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id    UUID NOT NULL REFERENCES trials(id) ON DELETE CASCADE,
    assigned_to UUID NOT NULL REFERENCES users(id),

    title       TEXT NOT NULL,
    description TEXT,
    due_at      TIMESTAMPTZ,

    -- Статус: pending | in_progress | completed | missed
    status      TEXT NOT NULL DEFAULT 'pending',

    completed_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_trial_tasks_trial_id ON trial_tasks(trial_id);
CREATE INDEX idx_trial_tasks_assigned_to ON trial_tasks(assigned_to);

-- ─────────────────────────────────────────────
-- Trial Events
-- Behavioral telemetry: все события в trial
-- ─────────────────────────────────────────────
CREATE TABLE trial_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id    UUID NOT NULL REFERENCES trials(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id),

    -- Тип события: task_completed | message_sent | deadline_missed |
    --              check_in | review_submitted | trial_abandoned | custom
    event_type  TEXT NOT NULL,

    -- Дополнительные данные события (JSON)
    payload     JSONB,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_trial_events_trial_id ON trial_events(trial_id);
CREATE INDEX idx_trial_events_user_id ON trial_events(user_id);
CREATE INDEX idx_trial_events_type ON trial_events(event_type);
CREATE INDEX idx_trial_events_occurred_at ON trial_events(occurred_at DESC);

-- ─────────────────────────────────────────────
-- Trigger: auto-update updated_at
-- ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_founder_profiles_updated_at
    BEFORE UPDATE ON founder_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_match_candidates_updated_at
    BEFORE UPDATE ON match_candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trials_updated_at
    BEFORE UPDATE ON trials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trial_tasks_updated_at
    BEFORE UPDATE ON trial_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
