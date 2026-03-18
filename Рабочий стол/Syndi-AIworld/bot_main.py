#!/usr/bin/env python3
import logging
import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

# Aiogram imports
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message

# Scheduler imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

# Project imports
from routers import setup_routers
from core.ai.recommender import generate_full_profile_summary
from core.user.profile_io import load_profile
from handlers.recommend import send_daily_recommendations
from config import Config

# ======================
# Logger Configuration
# ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Reduce noise from aiogram internal logs
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.INFO)

# ======================
# Environment Setup
# ======================
load_dotenv()

TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.critical("TELEGRAM_TOKEN not found in environment variables")
    raise ValueError("TELEGRAM_TOKEN is required")

# ======================
# Bot Initialization (aiogram 3.7.0+ compatible)
# ======================
bot_properties = DefaultBotProperties(
    parse_mode=ParseMode.HTML,
    link_preview_is_disabled=True,
    protect_content=False
)

bot: Bot = Bot(
    token=TELEGRAM_TOKEN,
    default=bot_properties
)
dp: Dispatcher = Dispatcher()

# ======================
# Command Handlers
# ======================
@dp.message(Command("start"))
async def handle_start_command(message: Message) -> None:
    """Handle /start command"""
    await message.answer(
        "🌌 <b>Добро пожаловать в психо-эзотерического бота!</b>\n\n"
        "Используйте /help для списка команд"
    )

@dp.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    """Handle /help command"""
    help_text = (
        "🆘 <b>Доступные команды:</b>\n\n"
        "/start - Начало работы\n"
        "/help - Эта справка\n"
        "/test - Проверка работы бота\n"
        "/summary - Ваш полный профиль\n"
        "/recommend - Получить рекомендацию\n"
        "/trigger - Тест ежедневных рекомендаций"
    )
    await message.answer(help_text)

@dp.message(Command("test"))
async def handle_test_command(message: Message) -> None:
    """Test bot functionality"""
    await message.answer("✅ <b>Бот работает корректно!</b>")

@dp.message(Command("trigger"))
async def handle_trigger_command(message: Message) -> None:
    """Manually trigger daily recommendations"""
    try:
        await send_daily_recommendations(bot, message.from_user.id)
        await message.answer("🔔 <b>Рекомендации успешно отправлены!</b>")
    except Exception as e:
        logger.error(f"Trigger error: {e}")
        await message.answer(f"❌ <b>Ошибка:</b> {str(e)}")

@dp.message(Command("summary"))
async def handle_summary_command(message: Message) -> None:
    """Generate full profile summary"""
    try:
        profile = await load_profile(bot, message.from_user.id)
        if not profile:
            await message.answer("❌ Профиль не найден")
            return
            
        summary = await generate_full_profile_summary(profile)
        await message.answer(
            f"📊 <b>Ваш полный профиль:</b>\n\n{summary}"
        )
    except Exception as e:
        logger.error(f"Summary error: {e}")
        await message.answer("❌ Не удалось сгенерировать профиль")

# ======================
# Router Setup
# ======================
try:
    setup_routers(dp)
    logger.info("All routers successfully initialized")
except Exception as e:
    logger.critical(f"Router setup error: {e}")
    raise

# ======================
# Scheduler Configuration
# ======================
scheduler = AsyncIOScheduler(
    jobstores={'default': MemoryJobStore()},
    timezone="Europe/Moscow"
)

# Daily recommendation at 9:00 AM
scheduler.add_job(
    func=lambda: asyncio.create_task(send_daily_recommendations(bot)),
    trigger='cron',
    hour=9,
    minute=0,
    name="daily_recommendations",
    misfire_grace_time=3600
)

# Debug job (runs every hour in debug mode)
if hasattr(Config, 'DEBUG') and Config.DEBUG:
    scheduler.add_job(
        func=lambda: asyncio.create_task(
            send_daily_recommendations(bot, Config.ADMIN_ID)
        ),
        trigger='interval',
        minutes=60,
        name="debug_recommendations"
    )

# ======================
# Main Application
# ======================
async def main() -> None:
    """Main application entry point"""
    try:
        logger.info("Starting bot...")
        
        if Config.DEBUG:
            logger.warning("Running in DEBUG mode!")
            await bot.send_message(
                chat_id=Config.ADMIN_ID,
                text="🔄 <b>Бот запущен в режиме отладки</b>"
            )
        
        scheduler.start()
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        raise
    finally:
        if scheduler.running:
            scheduler.shutdown()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        raise
