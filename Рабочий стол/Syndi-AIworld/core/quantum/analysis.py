from models import UserProfile
import random
print("[DEBUG] Запуск analysis.py")


def analyze_quantum_paths(profile: UserProfile) -> list:
    """
    Генерирует альтернативные сценарии жизни на основе профиля
    """
    mbti = profile.mbti or "INFP"
    enneagram = profile.enneagram or "Тип 4"
    tarot = profile.tarot_archetypes[0]["name"] if profile.tarot_archetypes else "Шут"
    psychomatrix = profile.psychomatrix or {}

    base_paths = [
        {
            "title": "Путь Тени",
            "description": f"Если бы вы поддались своей Тени ({tarot}), вы бы выбрали путь избегания.",
            "conflict": "Подмена истинных целей хаотичными импульсами.",
            "lesson": "Даже хаос может быть инструментом.",
            "avatar": f"Альтер-эго: Клоун-Анархист ({mbti})",
            "probability": random.uniform(0.2, 0.5),
        },
        {
            "title": "Путь Героя",
            "description": f"С вашим архетипом ({tarot}) и типом {enneagram}, вы бы встали на путь защиты других.",
            "conflict": "Жертвуете собой ради одобрения.",
            "lesson": "Вы заслуживаете заботы так же, как и другие.",
            "avatar": f"Альтер-эго: Спасатель без маски ({mbti})",
            "probability": random.uniform(0.2, 0.5),
        },
        {
            "title": "Путь Архиватора",
            "description": f"С интеллектом по психоматрице ({psychomatrix.get('7', 'Н/Д')}), вы могли бы уйти в наблюдение.",
            "conflict": "Погружение в анализ вместо действий.",
            "lesson": "Истина раскрывается в практике.",
            "avatar": f"Альтер-эго: Мудрец в башне ({mbti})",
            "probability": random.uniform(0.2, 0.5),
        },
    ]

    # Нормализуем вероятности
    total = sum(p["probability"] for p in base_paths)
    for p in base_paths:
        p["probability"] = round(p["probability"] / total, 2)

    return base_paths