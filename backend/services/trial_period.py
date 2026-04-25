"""
E3 — Trial Period AI

30-дневный пробный период после мэтча:
- Старт при создании матча
- Отслеживание активности (сообщения, встречи, аватар-взаимодействия)
- По истечении 30 дней без активности → режим view-only
- Полная интеграция с Telegram: уведомления на день 1, 7, 14, 25, 30
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)

TRIAL_DAYS = 30

# in-memory хранилище (заменяется на SQLAlchemy в B1)
# ключ: match_id, значение: TrialState dict
_trials: dict[int, dict] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _deadline(started_at: datetime) -> datetime:
    return started_at + timedelta(days=TRIAL_DAYS)


def _days_left(started_at: datetime) -> int:
    remaining = (_deadline(started_at) - _now()).total_seconds()
    return max(0, int(remaining // 86400))


# ---------------------------------------------------------------------------
# Публичный API
# ---------------------------------------------------------------------------

def start_trial(match_id: int, user_id_a: int, user_id_b: int) -> dict:
    """
    Запустить пробный период для пары.
    Вызывается из like_routes.py при создании матча.
    """
    if match_id in _trials:
        return get_trial_status(match_id)

    started_at = _now()
    state = {
        "match_id": match_id,
        "user_id_a": user_id_a,
        "user_id_b": user_id_b,
        "started_at": started_at,
        "expires_at": _deadline(started_at),
        "last_activity_a": None,
        "last_activity_b": None,
        "activity_count": 0,
        "mode": "active",       # active | view_only | expired
        "notified_days": [],    # уже отправленные reminder-уведомления
    }
    _trials[match_id] = state
    logger.info(f"[Trial] Started for match={match_id}, expires={state['expires_at'].isoformat()}")
    return _format(state)


def record_activity(match_id: int, user_id: int) -> dict:
    """
    Зафиксировать активность участника (сообщение, встреча, аватар-чат).
    Сбрасывает таймер неактивности.
    """
    state = _trials.get(match_id)
    if not state:
        raise KeyError(f"Trial not found: match_id={match_id}")

    if state["mode"] == "view_only":
        logger.info(f"[Trial] Activity after view_only for match={match_id} — restoring to active")
        state["mode"] = "active"

    now = _now()
    if state["user_id_a"] == user_id:
        state["last_activity_a"] = now
    elif state["user_id_b"] == user_id:
        state["last_activity_b"] = now
    else:
        raise ValueError(f"user_id={user_id} не принадлежит match={match_id}")

    state["activity_count"] += 1
    logger.info(f"[Trial] Activity recorded match={match_id} user={user_id} count={state['activity_count']}")
    return _format(state)


def get_trial_status(match_id: int) -> dict:
    """Получить текущий статус пробного периода."""
    state = _trials.get(match_id)
    if not state:
        raise KeyError(f"Trial not found: match_id={match_id}")
    _refresh_mode(state)
    return _format(state)


def check_all_trials() -> list[dict]:
    """
    Проверить все активные пробные периоды.
    Вызывается из планировщика (APScheduler) раз в час.
    Возвращает список действий: {match_id, action: 'notify'|'expire', days_left}
    """
    actions = []
    for match_id, state in _trials.items():
        if state["mode"] == "expired":
            continue

        days_left = _days_left(state["started_at"])
        _refresh_mode(state)

        # Напоминания: день 29, 23, 16, 7, 5 (за N дней до конца)
        remind_at_days = [29, 23, 16, 7, 5]
        for remind_day in remind_at_days:
            days_elapsed = TRIAL_DAYS - days_left
            # Отправляем при пересечении порога
            if days_elapsed >= remind_day and remind_day not in state["notified_days"]:
                state["notified_days"].append(remind_day)
                actions.append({
                    "match_id": match_id,
                    "user_id_a": state["user_id_a"],
                    "user_id_b": state["user_id_b"],
                    "action": "notify",
                    "days_left": days_left,
                    "days_elapsed": days_elapsed,
                    "remind_day": remind_day,
                })

        if state["mode"] in ("view_only", "expired"):
            actions.append({
                "match_id": match_id,
                "user_id_a": state["user_id_a"],
                "user_id_b": state["user_id_b"],
                "action": "expired" if state["mode"] == "expired" else "view_only",
                "days_left": 0,
            })

    return actions


def get_access_mode(match_id: int, user_id: int) -> str:
    """
    Проверить режим доступа для пользователя в рамках матча.
    Возвращает: 'full' | 'view_only' | 'not_found'
    """
    state = _trials.get(match_id)
    if not state:
        return "not_found"
    if user_id not in (state["user_id_a"], state["user_id_b"]):
        return "not_found"
    _refresh_mode(state)
    if state["mode"] in ("view_only", "expired"):
        return "view_only"
    return "full"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _refresh_mode(state: dict) -> None:
    """Обновить режим на основе истечения и активности."""
    if state["mode"] == "expired":
        return

    now = _now()
    expires_at = state["expires_at"]

    if now >= expires_at:
        # Нет активности совсем — view_only → expired
        if state["activity_count"] == 0:
            state["mode"] = "view_only"
        else:
            state["mode"] = "expired"   # период закончился, но активность была — просто истёк
        return

    # Ещё в пределах 30 дней
    # Проверяем: нет ли «мёртвого» периода (оба не активны > 14 дней подряд)
    last_a = state["last_activity_a"]
    last_b = state["last_activity_b"]

    # Если никто не активен и прошло > 14 дней с старта — ставим view_only
    if last_a is None and last_b is None:
        days_elapsed = (now - state["started_at"]).days
        if days_elapsed >= 14:
            state["mode"] = "view_only"
            logger.info(f"[Trial] match={state['match_id']} → view_only (14 days inactivity)")


def _format(state: dict) -> dict:
    now = _now()
    days_left = _days_left(state["started_at"])
    return {
        "match_id": state["match_id"],
        "mode": state["mode"],
        "days_left": days_left,
        "activity_count": state["activity_count"],
        "started_at": state["started_at"].isoformat(),
        "expires_at": state["expires_at"].isoformat(),
        "last_activity_a": state["last_activity_a"].isoformat() if state["last_activity_a"] else None,
        "last_activity_b": state["last_activity_b"].isoformat() if state["last_activity_b"] else None,
        "notified_days": state["notified_days"],
    }
