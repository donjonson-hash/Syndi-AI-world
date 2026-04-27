"""
Unit-тесты для telegram_bot (D6).
Не требуют реального Telegram токена и не запускают polling.
"""
import pytest

from telegram_bot import notifications as tg_notif


@pytest.fixture(autouse=True)
def _reset_tg_maps():
    """Очищаем in-memory маппинги между тестами."""
    tg_notif._tg_to_syndi.clear()
    tg_notif._syndi_to_tg.clear()
    yield
    tg_notif._tg_to_syndi.clear()
    tg_notif._syndi_to_tg.clear()


def test_notifications_link_telegram():
    tg_notif.link_telegram(telegram_id=12345, syndi_user_id=42)
    assert tg_notif.get_telegram_id(42) == 12345
    assert tg_notif.get_syndi_user_id(12345) == 42


def test_notifications_get_unknown():
    assert tg_notif.get_telegram_id(999) is None
    assert tg_notif.get_syndi_user_id(999) is None


async def test_send_notification_no_token(monkeypatch):
    """Без SYNDI_TELEGRAM_TOKEN → возвращает False, не падает."""
    monkeypatch.delenv("SYNDI_TELEGRAM_TOKEN", raising=False)
    tg_notif.link_telegram(telegram_id=111, syndi_user_id=1)
    ok = await tg_notif.send_match_notification(
        syndi_user_id=1, partner_name="Alice", match_score=88.0
    )
    assert ok is False


async def test_send_notification_no_mapping(monkeypatch):
    """Нет маппинга tg_id → возвращает False."""
    monkeypatch.setenv("SYNDI_TELEGRAM_TOKEN", "fake-token")
    ok = await tg_notif.send_match_notification(
        syndi_user_id=9999, partner_name="Bob", match_score=50.0
    )
    assert ok is False


async def test_send_like_notification_no_token(monkeypatch):
    monkeypatch.delenv("SYNDI_TELEGRAM_TOKEN", raising=False)
    tg_notif.link_telegram(telegram_id=222, syndi_user_id=2)
    ok = await tg_notif.send_like_notification(syndi_user_id=2, from_name="Charlie")
    assert ok is False


def test_bot_module_importable():
    """Импорт bot.py не должен падать при отсутствии токена."""
    from telegram_bot.bot import TELEGRAM_TOKEN, WELCOME_TEXT, HELP_TEXT
    assert isinstance(TELEGRAM_TOKEN, str)
    assert "Kristina" in WELCOME_TEXT
    assert "/help" in WELCOME_TEXT
    assert "команды" in HELP_TEXT.lower()


def test_bot_disabled_without_token(monkeypatch, caplog):
    """main() без токена → graceful exit, только warning в логах."""
    monkeypatch.setenv("SYNDI_TELEGRAM_TOKEN", "")
    from telegram_bot import bot as bot_mod
    monkeypatch.setattr(bot_mod, "TELEGRAM_TOKEN", "")

    import logging
    with caplog.at_level(logging.WARNING):
        bot_mod.main()
    assert any("not set" in r.message.lower() or "disabled" in r.message.lower()
               for r in caplog.records)
