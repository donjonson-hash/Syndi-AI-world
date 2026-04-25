"""
E3 — Trial Period API Routes

POST /api/trial/start          — запустить пробный период (вызывается автоматически при матче)
GET  /api/trial/status/{id}    — статус пробного периода
POST /api/trial/activity       — зафиксировать активность
GET  /api/trial/access/{id}    — проверить режим доступа текущего пользователя
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services.trial_period import (
    start_trial,
    record_activity,
    get_trial_status,
    get_access_mode,
)
from ..telegram_bot.trial_notifications import (
    send_trial_started,
    send_trial_activity_confirmed,
)
from ..telegram_bot.notifications import get_telegram_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trial", tags=["trial"])


class TrialStartRequest(BaseModel):
    match_id: int
    user_id_a: int
    user_id_b: int
    partner_name_a: str = "Партнёр"  # имя, которое видит пользователь A
    partner_name_b: str = "Партнёр"  # имя, которое видит пользователь B


class ActivityRequest(BaseModel):
    match_id: int
    user_id: int
    activity_type: str = "message"  # message | meeting | avatar_chat


@router.post("/start")
async def api_start_trial(req: TrialStartRequest):
    """Запустить пробный период для пары после мэтча."""
    try:
        status = start_trial(req.match_id, req.user_id_a, req.user_id_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Telegram-уведомления обоим участникам (non-blocking)
    try:
        await send_trial_started(req.user_id_a, req.match_id, req.partner_name_a)
        await send_trial_started(req.user_id_b, req.match_id, req.partner_name_b)
    except Exception as e:
        logger.warning(f"[Trial] Telegram start notification failed: {e}")

    return {"ok": True, "trial": status}


@router.get("/status/{match_id}")
async def api_trial_status(match_id: int):
    """Получить статус пробного периода по match_id."""
    try:
        return get_trial_status(match_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Trial not found: match_id={match_id}")


@router.post("/activity")
async def api_record_activity(req: ActivityRequest):
    """Зафиксировать активность участника. Восстанавливает доступ если был view-only."""
    try:
        prev_status = get_trial_status(req.match_id)
        was_view_only = prev_status["mode"] == "view_only"

        status = record_activity(req.match_id, req.user_id)

        # Если восстановились из view_only — уведомить
        if was_view_only and status["mode"] == "active":
            try:
                await send_trial_activity_confirmed(req.user_id, req.match_id)
            except Exception as e:
                logger.warning(f"[Trial] restore notification failed: {e}")

        return {"ok": True, "trial": status, "activity_type": req.activity_type}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Trial not found: match_id={req.match_id}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/access/{match_id}")
async def api_check_access(match_id: int, user_id: int):
    """Проверить режим доступа пользователя к матчу. full | view_only | not_found"""
    mode = get_access_mode(match_id, user_id)
    return {
        "match_id": match_id,
        "user_id": user_id,
        "mode": mode,
        "can_message": mode == "full",
        "can_view": mode in ("full", "view_only"),
    }
