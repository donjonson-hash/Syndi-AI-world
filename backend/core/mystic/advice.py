"""
Quantum Advice — генерация персонализированных советов на основе профиля.
"""
import random
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class MysticUserProfile:
    """Минимальный профиль для мистического модуля."""
    mbti: Optional[str] = None
    enneagram: Optional[str] = None
    psychomatrix: Optional[Dict[str, Any]] = None
    tarot_archetypes: Optional[list] = None


def generate_quantum_advice(profile: MysticUserProfile) -> str:
    """Генерирует персонализированный совет на основе профиля."""
    advices = {
        "conservative": [
            "Доверьтесь проверенным методам сегодня",
            "Стабильность - ваш ключ к успеху",
        ],
        "creative": [
            "Попробуйте новый подход к старой проблеме",
            "Ваше творчество сейчас на пике",
        ],
        "risk": [
            "Сделайте то, что обычно избегаете",
            "Риск может привести к неожиданным возможностям",
        ],
    }

    # Выбор типа совета на основе данных пользователя
    if profile.mbti and "P" in profile.mbti:
        category = "creative"
    elif profile.psychomatrix and profile.psychomatrix.get("3", 0) > 5:
        category = "risk"
    else:
        category = "conservative"

    logger.info(f"Quantum advice category: {category}")
    return random.choice(advices[category]) + f"\n\n(Выбор: {category})"
