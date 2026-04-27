"""
E3 — Trial Period Scheduler

APScheduler задача: каждый час проверяем все активные trial-периоды,
отправляем Telegram-уведомления по расписанию.
"""
from __future__ import annotations

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.trial_period import check_all_trials
# telegram_bot imported lazily inside _run_trial_check

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _run_trial_check() -> None:
    """Выполняется каждый час планировщиком."""
    from telegram_bot.trial_notifications import (
        send_trial_reminder, send_trial_expired, send_trial_view_only,
    )
    actions = check_all_trials()
    for action in actions:
        match_id = action["match_id"]
        uid_a = action["user_id_a"]
        uid_b = action["user_id_b"]

        try:
            if action["action"] == "notify":
                days_left = action["days_left"]
                await send_trial_reminder(uid_a, match_id, days_left)
                await send_trial_reminder(uid_b, match_id, days_left)

            elif action["action"] == "view_only":
                await send_trial_view_only(uid_a, match_id)
                await send_trial_view_only(uid_b, match_id)

            elif action["action"] == "expired":
                await send_trial_expired(uid_a, match_id)
                await send_trial_expired(uid_b, match_id)

        except Exception as e:
            logger.error(f"[TrialScheduler] Error for match={match_id}: {e}")


def start_trial_scheduler() -> None:
    """Запустить планировщик. Вызывается из main.py при старте приложения."""
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_trial_check,
        trigger="interval",
        hours=1,
        id="trial_check",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("[TrialScheduler] Started — checking trials every hour")


def stop_trial_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[TrialScheduler] Stopped")


# Compatibility alias for tests
class TrialScheduler:
    """Thin wrapper used by tests."""
    def start(self):
        start_trial_scheduler()

    def run(self):
        start_trial_scheduler()

    def check_expired(self):
        from services.trial_period import check_all_trials
        return check_all_trials()
