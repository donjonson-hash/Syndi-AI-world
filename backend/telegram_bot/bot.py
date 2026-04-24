#!/usr/bin/env python3
"""
Syndi AI Telegram Bot
Уведомления о матчах + чат с Kristina-аватаром.
Запуск: python telegram_bot/bot.py
"""
import os
import asyncio
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("SYNDI_TELEGRAM_TOKEN", "")

WELCOME_TEXT = (
    "👋 Привет! Я Kristina — твой AI-напарник в Syndi.\n\n"
    "Помогу найти идеального со-фаундера и буду рядом на каждом шагу.\n\n"
    "Команды:\n"
    "/profile — мой профиль\n"
    "/avatar — мой AI-аватар\n"
    "/matches — мои матчи\n"
    "/connect <user_id> — привязать аккаунт Syndi\n"
    "/help — все команды\n\n"
    "Или просто напиши мне — отвечу как Kristina ✨"
)

HELP_TEXT = (
    "📖 Доступные команды:\n\n"
    "/start — приветствие и меню\n"
    "/profile — показать твой Syndi профиль\n"
    "/avatar — твой AI-аватар (роль, настроение)\n"
    "/matches — список матчей\n"
    "/connect <user_id> — связать Telegram с Syndi аккаунтом\n"
    "/help — эта справка\n\n"
    "Просто пиши мне текстом — я отвечу как Kristina."
)


# ─── Kristina integration (lazy) ─────────────────────────────────────────────

_kristina = None


def _get_kristina():
    global _kristina
    if _kristina is None:
        from agents.kristina import KristinaUXDesigner
        _kristina = KristinaUXDesigner()
    return _kristina


# ─── Handlers ────────────────────────────────────────────────────────────────

async def start_handler(update, context):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("🤖 Мой аватар", callback_data="avatar")],
        [InlineKeyboardButton("💬 Чат с Kristina", callback_data="chat")],
        [InlineKeyboardButton("❤️ Мои матчи", callback_data="matches")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup)


async def help_handler(update, context):
    await update.message.reply_text(HELP_TEXT)


async def connect_handler(update, context):
    from telegram_bot.notifications import link_telegram
    args = context.args if hasattr(context, "args") else []
    if not args:
        await update.message.reply_text(
            "Использование: /connect <user_id>\n"
            "user_id — это твой Syndi ID (число)."
        )
        return
    try:
        syndi_user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("user_id должен быть числом.")
        return

    tg_id = update.effective_user.id
    link_telegram(tg_id, syndi_user_id)
    await update.message.reply_text(
        f"✅ Аккаунт связан! Syndi user_id = {syndi_user_id}.\n"
        f"Теперь ты будешь получать уведомления о матчах."
    )


async def profile_handler(update, context):
    from telegram_bot.notifications import get_syndi_user_id
    tg_id = update.effective_user.id
    syndi_user_id = get_syndi_user_id(tg_id)

    if not syndi_user_id:
        await update.message.reply_text(
            "Сначала привяжи аккаунт: /connect <user_id>"
        )
        return

    try:
        from database.database import AsyncSessionLocal
        from database import crud
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_id(db, syndi_user_id)
            if not user:
                await update.message.reply_text(f"Пользователь {syndi_user_id} не найден.")
                return
            fp = await crud.get_founder_profile_by_user_id(db, syndi_user_id)

        text = f"👤 <b>{user.name or 'Founder'}</b>\nID: {syndi_user_id}\n"
        if fp and fp.normalized_profile:
            norm = fp.normalized_profile
            role = norm.get("primary_role", "—")
            intent = norm.get("intent_goal", "—")
            text += f"Роль: {role}\nЦель: {intent}\n"
        else:
            text += "\n(Профиль основателя ещё не заполнен)"
        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"profile_handler failed: {e}")
        await update.message.reply_text("Не удалось загрузить профиль.")


async def avatar_handler(update, context):
    from telegram_bot.notifications import get_syndi_user_id
    tg_id = update.effective_user.id
    syndi_user_id = get_syndi_user_id(tg_id)

    if not syndi_user_id:
        await update.message.reply_text(
            "Сначала привяжи аккаунт: /connect <user_id>"
        )
        return

    try:
        from avatar_platform.avatar_factory import AvatarFactory
        avatar = AvatarFactory.get_avatar(syndi_user_id)
        if not avatar:
            await update.message.reply_text(
                "У тебя пока нет AI-аватара. Он создаётся автоматически при первом матче."
            )
            return
        text = (
            f"🤖 <b>AI-аватар</b>\n"
            f"Имя: {avatar.get('founder_name', '—')}\n"
            f"Роль: {avatar.get('role_id', '—')}\n"
            f"Настроение: {avatar.get('mood', 'нейтральное')}"
        )
        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"avatar_handler failed: {e}")
        await update.message.reply_text("Не удалось загрузить аватар.")


async def matches_handler(update, context):
    from telegram_bot.notifications import get_syndi_user_id
    tg_id = update.effective_user.id
    syndi_user_id = get_syndi_user_id(tg_id)

    if not syndi_user_id:
        await update.message.reply_text(
            "Сначала привяжи аккаунт: /connect <user_id>"
        )
        return

    try:
        from database.database import AsyncSessionLocal
        from database import crud
        async with AsyncSessionLocal() as db:
            matches = await crud.list_matches_for_user(db, syndi_user_id)

        if not matches:
            await update.message.reply_text("Пока матчей нет. Свайпай в Syndi!")
            return

        lines = ["❤️ <b>Твои матчи:</b>\n"]
        for m in matches[:10]:
            partner_id = m.user_b_id if m.user_a_id == syndi_user_id else m.user_a_id
            score = m.match_score or 0
            lines.append(f"• Founder {partner_id} — {score:.0f}%")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        logger.warning(f"matches_handler failed: {e}")
        await update.message.reply_text("Не удалось загрузить матчи.")


async def chat_handler(update, context):
    """Любое текстовое сообщение → передать в Kristina."""
    text = update.message.text or ""
    user_id = update.effective_user.id
    session_id = f"tg_{user_id}"
    try:
        kristina = _get_kristina()
        response = await kristina.process_message(session_id, text)
        await update.message.reply_text(response.content)
    except Exception as e:
        logger.warning(f"chat_handler failed: {e}")
        await update.message.reply_text(
            "Упс, что-то не так. Попробуй ещё раз через минуту."
        )


async def callback_query_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "profile":
        await query.message.reply_text("Команда: /profile")
    elif data == "avatar":
        await query.message.reply_text("Команда: /avatar")
    elif data == "chat":
        await query.message.reply_text("Просто напиши мне что угодно — я отвечу как Kristina ✨")
    elif data == "matches":
        await query.message.reply_text("Команда: /matches")


# ─── Main ────────────────────────────────────────────────────────────────────

PROXY_URL = os.getenv("HTTPS_PROXY", os.getenv("https_proxy", ""))


def build_application(token: str):
    """Собрать Application с хендлерами. Импорт telegram — внутри функции."""
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        filters,
    )
    builder = Application.builder().token(token)
    if PROXY_URL:
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(proxy=PROXY_URL)
        builder = builder.request(request)
        logger.info(f"Using proxy: {PROXY_URL}")
    app = builder.build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("connect", connect_handler))
    app.add_handler(CommandHandler("profile", profile_handler))
    app.add_handler(CommandHandler("avatar", avatar_handler))
    app.add_handler(CommandHandler("matches", matches_handler))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    return app


def main() -> None:
    """Запуск бота (блокирующий polling)."""
    if not TELEGRAM_TOKEN:
        logger.warning("SYNDI_TELEGRAM_TOKEN not set — bot disabled")
        return

    logger.info("Starting Syndi Telegram bot...")
    app = build_application(TELEGRAM_TOKEN)
    app.run_polling()


if __name__ == "__main__":
    main()
