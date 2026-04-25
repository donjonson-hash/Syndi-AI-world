"""
E3 — Тесты Trial Period AI
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock

from backend.services.trial_period import (
    start_trial,
    record_activity,
    get_trial_status,
    get_access_mode,
    check_all_trials,
    _trials,
    TRIAL_DAYS,
)


@pytest.fixture(autouse=True)
def clear_trials():
    """Чистим глобальный стор перед каждым тестом."""
    _trials.clear()
    yield
    _trials.clear()


class TestStartTrial:
    def test_start_creates_trial(self):
        status = start_trial(match_id=1, user_id_a=10, user_id_b=20)
        assert status["match_id"] == 1
        assert status["mode"] == "active"
        assert status["days_left"] == TRIAL_DAYS
        assert status["activity_count"] == 0

    def test_start_idempotent(self):
        start_trial(1, 10, 20)
        start_trial(1, 10, 20)  # повторный вызов
        assert len(_trials) == 1

    def test_expires_at_30_days(self):
        status = start_trial(1, 10, 20)
        started = datetime.fromisoformat(status["started_at"])
        expires = datetime.fromisoformat(status["expires_at"])
        assert (expires - started).days == TRIAL_DAYS


class TestRecordActivity:
    def test_record_user_a(self):
        start_trial(1, 10, 20)
        status = record_activity(1, 10)
        assert status["activity_count"] == 1
        assert status["last_activity_a"] is not None
        assert status["last_activity_b"] is None

    def test_record_user_b(self):
        start_trial(1, 10, 20)
        record_activity(1, 10)
        status = record_activity(1, 20)
        assert status["activity_count"] == 2
        assert status["last_activity_b"] is not None

    def test_record_unknown_user_raises(self):
        start_trial(1, 10, 20)
        with pytest.raises(ValueError):
            record_activity(1, 99)

    def test_record_unknown_match_raises(self):
        with pytest.raises(KeyError):
            record_activity(999, 10)

    def test_view_only_restored_on_activity(self):
        start_trial(1, 10, 20)
        # Форсируем view_only
        _trials[1]["mode"] = "view_only"
        status = record_activity(1, 10)
        assert status["mode"] == "active"


class TestAccessMode:
    def test_full_access_by_default(self):
        start_trial(1, 10, 20)
        assert get_access_mode(1, 10) == "full"
        assert get_access_mode(1, 20) == "full"

    def test_view_only_when_expired(self):
        start_trial(1, 10, 20)
        _trials[1]["mode"] = "view_only"
        assert get_access_mode(1, 10) == "view_only"

    def test_not_found_for_wrong_match(self):
        assert get_access_mode(999, 10) == "not_found"

    def test_not_found_for_wrong_user(self):
        start_trial(1, 10, 20)
        assert get_access_mode(1, 99) == "not_found"


class TestInactivityViewOnly:
    def test_view_only_after_14_days_inactivity(self):
        """Если никто не активен 14+ дней — переходим в view_only."""
        start_trial(1, 10, 20)
        # Симулируем 15 дней назад
        past = datetime.now(timezone.utc) - timedelta(days=15)
        _trials[1]["started_at"] = past

        status = get_trial_status(1)
        assert status["mode"] == "view_only"

    def test_active_if_within_14_days(self):
        start_trial(1, 10, 20)
        past = datetime.now(timezone.utc) - timedelta(days=10)
        _trials[1]["started_at"] = past

        status = get_trial_status(1)
        assert status["mode"] == "active"

    def test_no_view_only_if_has_activity(self):
        """Если есть активность — view_only не ставится даже после 14 дней."""
        start_trial(1, 10, 20)
        past = datetime.now(timezone.utc) - timedelta(days=20)
        _trials[1]["started_at"] = past
        _trials[1]["last_activity_a"] = datetime.now(timezone.utc) - timedelta(days=1)
        _trials[1]["activity_count"] = 1

        status = get_trial_status(1)
        # Активность была — не view_only (если 30 дней не истекли)
        assert status["mode"] in ("active", "expired")


class TestSchedulerActions:
    def test_check_generates_notify_action(self):
        """Проверяем что scheduler генерирует notify на нужных порогах."""
        start_trial(1, 10, 20)
        past = datetime.now(timezone.utc) - timedelta(days=8)
        _trials[1]["started_at"] = past
        _trials[1]["expires_at"] = past + timedelta(days=TRIAL_DAYS)

        actions = check_all_trials()
        notify_actions = [a for a in actions if a["action"] == "notify"]
        assert len(notify_actions) >= 1

    def test_check_generates_view_only_action(self):
        start_trial(1, 10, 20)
        _trials[1]["mode"] = "view_only"
        actions = check_all_trials()
        view_actions = [a for a in actions if a["action"] == "view_only"]
        assert len(view_actions) == 1
