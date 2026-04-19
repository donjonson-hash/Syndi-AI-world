from handlers.profile import UserProfile
import random
print("[DEBUG] Запуск advice.py")


def generate_quantum_advice(profile: UserProfile) -> str:
    """Генерирует персонализированный совет"""
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

    return random.choice(advices[category]) + f"\n\n(Выбор: {category})"

    # В handlers.py


logging.info(f"Quantum request from {callback.from_user.id} at {datetime.now()}")