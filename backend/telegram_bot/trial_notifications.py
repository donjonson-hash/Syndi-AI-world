"""
E3 — Telegram Trial Period Notifications

Уведомления пробного периода для @krississtigai_bot:
- Старт пробного периода
- Напоминания (за 7, 14, 25 дней)
- Переход в view-only (нет активности)
- Истечение периода
- Активность зафиксирована
"""
from __future__ import annotations

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _token() -> Optional[str]:
    return os.getenv("SYNDI_TELEGRAM_TOKEN") or None


async def _send(tg_id: int, text: str, parse_mode: str = "HTML") -> bool:
    token = _token()
    if not token:
        return False
    try:
        import httpx
        proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        kwargs = {"proxies": proxy} if proxy else {}
        async with httpx.AsyncClient(**kwargs) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": tg_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True,
                },
                timeout=8.0,
            )
            if r.status_code != 200:
                logger.warning(f"[TG Trial] HTTP {r.status_code}: {r.text[:200]}")
                return False
        return True
    except Exception as e:
        logger.warning(f"[TG Trial] send failed: {e}")
        return False


def _resolve_tg_id(syndi_user_id: int) -> Optional[int]:
    """Получить Telegram ID по Syndi user_id."""
    from .notifications import get_telegram_id
    return get_telegram_id(syndi_user_id)


async def send_trial_started(syndi_user_id: int, match_id: int, partner_name: str) -> bool:
    """Уведомление о начале пробного периода."""
    tg_id = _resolve_tg_id(syndi_user_id)
    if not tg_id:
        return False
    text = (
        f"🚀 <b>Пробный период начался!</b>\n\n"
        f"👥 Твой потенциальный со-фаундер: <b>{partner_name}</b>\n"
        f"⏳ У тебя <b>30 дней</b> чтобы познакомиться поближе.\n\n"
        f"💬 Общайтесь, встречайтесь, задавайте вопросы — ваши аватары помогут!\n"
        f"📌 Матч #{match_id}"
    )
    return await _send(tg_id, text)


async def send_trial_reminder(syndi_user_id: int, match_id: int, days_left: int) -> bool:
    """Напоминание с количеством оставшихся дней."""
    tg_id = _resolve_tg_id(syndi_user_id)
    if not tg_id:
        return False

    if days_left > 14:
        emoji = "💡"
        urgency = "Не забудь познакомиться с партнёром!"
    elif days_left > 7:
        emoji = "⚠️"
        urgency = "Самое время для первой встречи!"
    elif days_left > 3:
        emoji = "🔔"
        urgency = "Торопись — скоро только режим просмотра!"
    else:
        emoji = "🚨"
        urgency = "Последние дни! Покажи активность чтобы сохранить доступ."

    text = (
        f"{emoji} <b>Напоминание о пробном периоде</b>\n\n"
        f"⏳ Осталось <b>{days_left} дн.</b> до конца пробного периода.\n"
        f"📌 Матч #{match_id}\n\n"
        f"{urgency}\n\n"
        f"Открой Syndi и пообщайся с аватаром партнёра!"
    )
    return await _send(tg_id, text)


async def send_trial_view_only(syndi_user_id: int, match_id: int) -> bool:
    """Уведомление о переходе в режим view-only (нет активности)."""
    tg_id = _resolve_tg_id(syndi_user_id)
    if not tg_id:
        return False
    text = (
        f"😴 <b>Режим просмотра активирован</b>\n\n"
        f"По матчу #{match_id} не было активности в течение длительного времени.\n\n"
        f"🔒 Теперь доступен только <b>режим просмотра</b> — \n"
        f"ты можешь видеть профиль партнёра, но не можешь писать.\n\n"
        f"✅ <b>Чтобы восстановить полный доступ</b> — просто напиши сообщение "
        f"или взаимодействуй с аватаром партнёра в Syndi!"
    )
    return await _send(tg_id, text)


async def send_trial_expired(syndi_user_id: int, match_id: int) -> bool:
    """Уведомление об истечении 30-дневного периода с активностью."""
    tg_id = _resolve_tg_id(syndi_user_id)
    if not tg_id:
        return False
    text = (
        f"🎊 <b>Пробный период завершён!</b>\n\n"
        f"30 дней пробного периода по матчу #{match_id} истекли.\n\n"
        f"🤝 Вы проявляли активность — это отличный знак!\n"
        f"Свяжитесь напрямую или продолжайте общение через Syndi."
    )
    return await _send(tg_id, text)


async def send_trial_activity_confirmed(syndi_user_id: int, match_id: int) -> bool:
    """Тихое подтверждение активности (отправляется только если был view_only → active)."""
    tg_id = _resolve_tg_id(syndi_user_id)
    if not tg_id:
        return False
    text = (
        f"✅ <b>Доступ восстановлен!</b>\n\n"
        f"Твоя активность зафиксирована по матчу #{match_id}.\n"
        f"Полный доступ к общению восстановлен. Продолжай!"
    )
    return await _send(tg_id, text)
