"""
Kristina UX Designer Agent

В `process_message` сначала пытаемся получить ответ от LLMService (Mimo API).
Если LLM недоступен (нет ключа) или вернул пустую строку / упал — уходим
в keyword-fallback (прежняя логика).
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone

from .base import AgentRole, AgentResponse, MessageType, get_llm_client
from services.llm import get_llm_service
from avatar_platform.emotional_core import EmotionalCore
from avatar_platform.agent_router import detect_mode, AgentMode


class KristinaUXDesigner:
    def __init__(self):
        self.agent_id = "kristina_ux_001"
        self.name = "Кристина"
        self.role = AgentRole.UX_DESIGNER
        self.personality = "Дружелюбная, креативная"
        self.expertise = [
            "Design Systems",
            "Accessibility",
            "Mobile Design",
            "UX Design", "UI Design", "User Research",
            "Prototyping", "Design Thinking", "Figma"
        ]
        self.system_prompt = (
            "Ты Кристина — AI-ассистент SyndiAI, помогающий основателям находить "
            "со-фаундеров. Отвечай кратко, по-дружески, на русском языке. "
            "Разбираешься в UX, продуктовой разработке и командной динамике."
        )
        self.memories = {}
        self.total_conversations = 0
        self.llm_client = get_llm_client()
        self.llm_service = get_llm_service()
        self.emotional_core = EmotionalCore()

    def get_memory(self, user_id: str):
        if user_id not in self.memories:
            from .base import AgentMemory
            self.memories[user_id] = AgentMemory(user_id=user_id)
        return self.memories[user_id]

    def get_info(self) -> dict:
        return {
            "id": self.agent_id,
            "name": self.name,
            "role": self.role.value if hasattr(self.role, 'value') else str(self.role),
            "expertise": self.expertise,
            "personality": self.personality,
            "total_conversations": self.total_conversations,
            "active_users": len(self.memories)
        }

    def _detect_message_type(self, message: str) -> MessageType:
        message_lower = message.lower()
        if any(kw in message_lower for kw in ["код", "code", "python", "javascript"]):
            return MessageType.CODE
        if any(kw in message_lower for kw in ["дизайн", "design", "figma", "ui", "ux"]):
            return MessageType.DESIGN
        if any(kw in message_lower for kw in ["?", "как", "что", "почему"]):
            return MessageType.QUESTION
        if any(kw in message_lower for kw in ["совет", "advice", "помоги"]):
            return MessageType.ADVICE
        return MessageType.TEXT

    def _fallback_reply(self, message: str, mode: Optional[AgentMode] = None):
        """Keyword-логика. Возвращает (content, suggestions).

        Если передан `mode`, сначала проверяется режим-специфичный шаблон
        (EXECUTOR / MENTOR), затем классическая keyword-логика для ADVISOR.
        """
        prompt_lower = message.lower()

        if mode == AgentMode.EXECUTOR and any(
            kw in prompt_lower for kw in ("напиши", "составь", "сделай", "подготовь", "создай")
        ):
            return (
                "Вот готовый шаблон — используй и адаптируй под задачу:\n"
                "1. Контекст\n"
                "2. Цель\n"
                "3. Шаги\n"
                "4. Критерии готовности",
                [
                    "Нужен другой формат?",
                    "Добавить детали",
                    "Сделать чеклист",
                ],
            )

        if mode == AgentMode.MENTOR and any(
            kw in prompt_lower for kw in ("конфликт", "проблема", "сложно", "устал", "боюсь")
        ):
            return (
                "Понимаю, это непросто. Расскажи подробнее — что именно происходит "
                "и как ты сейчас себя чувствуешь? Разберёмся вместе.",
                [
                    "Как начать разговор?",
                    "Что сказать партнёру?",
                    "Как снизить напряжение?",
                ],
            )

        if "исследование" in prompt_lower or "research" in prompt_lower:
            return (
                "Исследование пользователей — это ключевой этап UX. Начните с интервью.",
                [
                    "Как составить план интервью?",
                    "Сколько пользователей нужно опросить?",
                    "Какие вопросы задавать?",
                ],
            )
        if "прототип" in prompt_lower or "prototype" in prompt_lower:
            return (
                "Прототипирование помогает быстро проверить идеи. Используйте Figma.",
                [
                    "Как начать в Figma?",
                    "Что такое wireframe?",
                    "Как тестировать прототипы?",
                ],
            )
        if "привет" in prompt_lower:
            return (
                "Привет! Рада тебя видеть. Чем могу помочь сегодня?",
                ["Расскажи о себе", "Что ты умеешь?", "Помоги с дизайном"],
            )
        if "help" in prompt_lower or "помоги" in prompt_lower:
            return (
                "Я могу помочь с UX-дизайном, исследованиями пользователей и прототипированием.",
                ["UX исследования", "Прототипирование", "Дизайн системы"],
            )
        if "проект" in prompt_lower:
            return (
                "Вот план работы над проектом:\n"
                "- Определите целевую аудиторию\n"
                "- Составьте User Stories\n"
                "- Создайте CJM",
                ["Как определить аудиторию?", "Что такое User Stories?", "Как создать CJM?"],
            )
        return (
            "Интересный вопрос! Давай разберёмся...",
            ["Узнать больше о UX", "Получить совет", "Обсудить проект"],
        )

    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None,
    ) -> AgentResponse:
        memory = self.get_memory(user_id)
        memory.add_message("user", message)

        msg_type = self._detect_message_type(message)

        routing = detect_mode(message)

        msg_lower = message.lower()
        tone_context = {
            "positive_tone": "хорошо" in msg_lower,
            "complex_question": "?" in message,
            "negative_tone": any(w in msg_lower for w in ["плохо", "не работает", "проблема"]),
        }
        emotional_state = self.emotional_core.evolve(context=tone_context)

        content: str = ""
        if self.llm_service is not None and getattr(self.llm_service, "api_key", ""):
            try:
                # Берём последние 10 сообщений как контекст (исключая только что добавленное
                # user-сообщение — оно передаётся как `prompt`).
                history = memory.get_context(10)[:-1]
                llm_context = [
                    {"role": m["role"], "content": m["content"]}
                    for m in history
                    if m.get("role") in ("user", "assistant")
                ]
                system_prompt = f"{routing.system_prompt}\n{emotional_state['llm_style_hint']}"
                content = await self.llm_service.generate_response(
                    prompt=message,
                    system_prompt=system_prompt,
                    context=llm_context,
                ) or ""
            except Exception:
                content = ""

        if not isinstance(content, str) or not content.strip():
            fb_content, suggestions = self._fallback_reply(message, mode=routing.mode)
            content = fb_content
        else:
            # Для LLM-ответа suggestions генерируем по keyword (чтобы UI не терял кнопки).
            _, suggestions = self._fallback_reply(message, mode=routing.mode)

        response = AgentResponse(
            content=content,
            message_type=msg_type,
            suggestions=suggestions[:3],
            actions=[
                {"type": "suggest", "label": "Получить совет", "payload": "advice"},
                {"type": "share", "label": "Поделиться", "payload": "share"},
            ],
            metadata={
                "mood_description": emotional_state["mood_description"],
                "dominant_emotion": emotional_state["dominant_emotion"],
                "mode": routing.mode.value,
            },
        )

        memory.add_message("assistant", content)
        self.total_conversations += 1
        return response