"""
Syndi Telegram Notifications — отправка уведомлений пользователям.
Используется из like_routes.py при создании матча.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# telegram_id -> user_id маппинг (in-memory для MVP)
_tg_to_syndi: dict = {}
_syndi_to_tg: dict = {}


def link_telegram(telegram_id: int, syndi_user_id: int) -> None:
    """Связать Telegram ID с Syndi user_id."""
    _tg_to_syndi[telegram_id] = syndi_user_id
    _syndi_to_tg[syndi_user_id] = telegram_id


def get_telegram_id(syndi_user_id: int) -> Optional[int]:
    return _syndi_to_tg.get(syndi_user_id)


def get_syndi_user_id(telegram_id: int) -> Optional[int]:
    return _tg_to_syndi.get(telegram_id)


async def send_match_notification(
    syndi_user_id: int,
    partner_name: str,
    match_score: float,
) -> bool:
    """Отправить уведомление о матче."""
    tg_id = get_telegram_id(syndi_user_id)
    if not tg_id:
        return False

    token = os.getenv("SYNDI_TELEGRAM_TOKEN", "")
    if not token:
        return False

    try:
        import httpx
        text = (
            f"🎉 Новый матч!\n\n"
            f"👤 Со-фаундер: {partner_name}\n"
            f"⭐ FounderFit: {match_score:.0f}%\n\n"
            f"Открой Syndi чтобы познакомиться!"
        )
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": tg_id, "text": text, "parse_mode": "HTML"},
                timeout=5.0,
            )
        return True
    except Exception as e:
        logger.warning(f"Telegram notification failed: {e}")
        return False


async def send_like_notification(
    syndi_user_id: int,
    from_name: str,
) -> bool:
    """Отправить уведомление о новом лайке."""
    tg_id = get_telegram_id(syndi_user_id)
    if not tg_id:
        return False

    token = os.getenv("SYNDI_TELEGRAM_TOKEN", "")
    if not token:
        return False

    try:
        import httpx
        text = (
            f"❤️ Новый лайк!\n\n"
            f"Тебя лайкнул {from_name}. Загляни в Syndi!"
        )
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": tg_id, "text": text},
                timeout=5.0,
            )
        return True
    except Exception as e:
        logger.warning(f"Telegram like notification failed: {e}")
        return False
