"""
Quantum Path Analysis — генерация альтернативных сценариев жизни.

Также содержит `compute_mystic_score` — оценку совместимости пары по
MBTI и эннеаграмме для использования в расширенном scoring.
"""
import random
from typing import Any, Dict, List, Optional

from .advice import MysticUserProfile
from .mbti import MBTI_TYPES


def analyze_quantum_paths(profile: MysticUserProfile) -> List[Dict[str, Any]]:
    """
    Генерирует альтернативные сценарии жизни на основе профиля.
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


def _coerce_enneagram(value: Any) -> Optional[int]:
    """enneagram в profile может быть int, str("4"), "4w5", "Тип 4" — приводим к 1..9."""
    if value is None:
        return None
    if isinstance(value, int):
        return value if 1 <= value <= 9 else None
    if isinstance(value, str):
        s = value.strip().lower()
        if not s:
            return None
        # Берём первую цифру 1..9
        for ch in s:
            if ch.isdigit() and ch != "0":
                try:
                    n = int(ch)
                except ValueError:
                    return None
                return n if 1 <= n <= 9 else None
    return None


def _mbti_score(mbti_a: Optional[str], mbti_b: Optional[str]) -> float:
    if not mbti_a or not mbti_b:
        return 50.0
    a = mbti_a.upper()
    b = mbti_b.upper()
    type_a = MBTI_TYPES.get(a)
    if type_a is None:
        return 50.0
    return 100.0 if b in type_a.compatible_with else 50.0


def _enneagram_score(a: Optional[int], b: Optional[int]) -> float:
    if a is None or b is None:
        return 50.0
    if a == b:
        return 60.0
    diff = abs(a - b)
    # Соседние типы на круге эннеаграммы: разница 1 или 8 (9→1 = 1, 1→9 = 8).
    if diff == 1 or diff == 8:
        return 80.0
    return 40.0


def compute_mystic_score(profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Вычисляет совместимость по MBTI и эннеаграмме.

    profile_a / profile_b — `normalized_profile` JSON (dict).

    Возвращает: {
        "mbti_score":       float (0..100),
        "enneagram_score":  float (0..100),
        "mystic_total":     float (0..100) = 0.6*mbti + 0.4*enneagram,
        "mbti_a":           str | None,
        "mbti_b":           str | None,
        "enneagram_a":      int | None,
        "enneagram_b":      int | None,
    }
    """
    pa = profile_a or {}
    pb = profile_b or {}

    mbti_a = pa.get("mbti_type") or pa.get("mbti")
    mbti_b = pb.get("mbti_type") or pb.get("mbti")
    if isinstance(mbti_a, str):
        mbti_a = mbti_a.upper().strip() or None
    if isinstance(mbti_b, str):
        mbti_b = mbti_b.upper().strip() or None

    enn_a = _coerce_enneagram(pa.get("enneagram_type") or pa.get("enneagram"))
    enn_b = _coerce_enneagram(pb.get("enneagram_type") or pb.get("enneagram"))

    mbti_s = _mbti_score(mbti_a, mbti_b)
    enn_s = _enneagram_score(enn_a, enn_b)
    mystic_total = round(0.6 * mbti_s + 0.4 * enn_s, 2)

    return {
        "mbti_score": mbti_s,
        "enneagram_score": enn_s,
        "mystic_total": mystic_total,
        "mbti_a": mbti_a if isinstance(mbti_a, str) else None,
        "mbti_b": mbti_b if isinstance(mbti_b, str) else None,
        "enneagram_a": enn_a,
        "enneagram_b": enn_b,
    }
