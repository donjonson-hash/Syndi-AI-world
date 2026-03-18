import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.debug("Запуск config.py")

# Загрузка .env файла
load_dotenv()

# Получение переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
IONQ_API_KEY = os.getenv("IONQ_API_KEY")
USE_REAL_QUANTUM = os.getenv("USE_REAL_QUANTUM", "True").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

class Config:
    BOT_TOKEN = BOT_TOKEN
    ADMIN_ID = ADMIN_ID
    DEEPSEEK_API_KEY = DEEPSEEK_API_KEY
    IONQ_API_KEY = IONQ_API_KEY
    USE_REAL_QUANTUM = USE_REAL_QUANTUM
    DEBUG = DEBUG_MODE

    @classmethod
    def verify_api_keys(cls):
        required_keys = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "ADMIN_ID": cls.ADMIN_ID
        }
        for name, value in required_keys.items():
            if not value:
                logger.error(f"❌ Не задан {name}")
                raise ValueError(f"Не задан {name}")
            logger.debug(f"{name} успешно загружен")
        
        if not cls.DEEPSEEK_API_KEY:
            logger.warning("⚠️ DEEPSEEK_API_KEY не задан")
