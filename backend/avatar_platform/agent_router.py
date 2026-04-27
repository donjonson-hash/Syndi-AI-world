"""
AgentRouter — маршрутизация запросов между режимами Kristina-аватара.
Адаптировано из kristina-revolutionary/agents/router.py (упрощённая версия).
"""
from enum import Enum
from dataclasses import dataclass


class AgentMode(str, Enum):
    ADVISOR  = "advisor"   # стратегические вопросы, бизнес, партнёрство
    MENTOR   = "mentor"    # конфликты, поддержка, сложные ситуации
    EXECUTOR = "executor"  # рутинные задачи по роли


# Ключевые слова для авто-выбора режима
_MODE_KEYWORDS = {
    AgentMode.MENTOR: [
        "конфликт", "поспорили", "не могу", "боюсь", "страх", "тревога",
        "сложно", "устал", "проблема", "помоги", "не знаю что делать",
        "разошлись", "непонимание", "обидно", "злюсь", "разочарован",
    ],
    AgentMode.EXECUTOR: [
        "напиши", "составь", "сделай", "подготовь", "создай",
        "написать", "составить", "сделать", "задача", "задание",
        "user story", "бэклог", "код", "тест", "миграция", "питч",
        "отчёт", "план", "roadmap", "чеклист",
    ],
    AgentMode.ADVISOR: [
        "стратегия", "решение", "партнёр", "со-фаундер", "инвестор",
        "как лучше", "что думаешь", "совет", "мнение", "оцени",
        "идея", "направление", "цель", "приоритет", "фокус",
    ],
}

# System prompts для каждого режима
MODE_SYSTEM_PROMPTS = {
    AgentMode.ADVISOR: """Ты Кристина — AI-советник со-фаундера в Syndi.
Твоя роль: помогать принимать стратегические решения о продукте, партнёрстве и бизнесе.
Давай структурированные советы: 1) анализ ситуации 2) варианты 3) рекомендация.
Будь конкретной, опирайся на данные. Задавай уточняющие вопросы если нужно.""",

    AgentMode.MENTOR: """Ты Кристина — ментор и поддержка для со-фаундера.
Твоя роль: помогать в конфликтных и сложных ситуациях внутри команды.
Будь эмпатичной, выслушай, задай уточняющие вопросы прежде чем давать советы.
Структура: понять → поддержать → помочь найти выход вместе.""",

    AgentMode.EXECUTOR: """Ты Кристина — исполнитель задач со-фаундера.
Твоя роль: помогать выполнять конкретные рабочие задачи по роли фаундера.
Давай чёткий результат: готовый текст, шаблон, чеклист или план.
Не объясняй лишнего — сразу выдавай результат.""",
}


@dataclass
class RoutingDecision:
    mode: AgentMode
    confidence: float
    system_prompt: str


def detect_mode(message: str) -> RoutingDecision:
    """Определить режим по ключевым словам в сообщении."""
    msg_lower = message.lower()
    scores = {mode: 0 for mode in AgentMode}

    for mode, keywords in _MODE_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                scores[mode] += 1

    best_mode = max(scores, key=scores.get)
    best_score = scores[best_mode]

    if best_score == 0:
        # Дефолт — советник
        best_mode = AgentMode.ADVISOR
        confidence = 0.3
    else:
        confidence = min(1.0, best_score * 0.3)

    return RoutingDecision(
        mode=best_mode,
        confidence=confidence,
        system_prompt=MODE_SYSTEM_PROMPTS[best_mode],
    )