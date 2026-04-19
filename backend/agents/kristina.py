"""
Kristina UX Designer Agent
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from .base import AgentRole, AgentResponse, MessageType, get_llm_client


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
        self.system_prompt = "Ты Kristina, UX Designer."
        self.memories = {}
        self.total_conversations = 0
        self.llm_client = get_llm_client()
    
    def get_memory(self, user_id: str):
        if user_id not in self.memories:
            from .base import AgentMemory
            self.memories[user_id] = AgentMemory(user_id=user_id)
        return self.memories[user_id]
    
    def get_info(self) -> dict:
        """ДОБАВИТЬ ЭТОТ МЕТОД"""
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
        """ДОБАВИТЬ ЭТОТ МЕТОД"""
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
    
    async def process_message(self, user_id: str, message: str, context: Optional[Dict] = None) -> AgentResponse:
        """ДОБАВИТЬ ЭТОТ МЕТОД"""
        memory = self.get_memory(user_id)
        memory.add_message("user", message)
        
        # Простая генерация ответа
        prompt_lower = message.lower()
        
        # Определяем тип сообщения и формируем ответ с suggestions
        msg_type = self._detect_message_type(message)
        
        if "исследование" in prompt_lower or "research" in prompt_lower:
            content = "Исследование пользователей — это ключевой этап UX. Начните с интервью."
            suggestions = [
                "Как составить план интервью?",
                "Сколько пользователей нужно опросить?",
                "Какие вопросы задавать?"
            ]
        elif "прототип" in prompt_lower or "prototype" in prompt_lower:
            content = "Прототипирование помогает быстро проверить идеи. Используйте Figma."
            suggestions = [
                "Как начать в Figma?",
                "Что такое wireframe?",
                "Как тестировать прототипы?"
            ]
        elif "привет" in prompt_lower:
            content = "Привет! Рада тебя видеть. Чем могу помочь сегодня?"
            suggestions = [
                "Расскажи о себе",
                "Что ты умеешь?",
                "Помоги с дизайном"
            ]
        elif "help" in prompt_lower or "помоги" in prompt_lower:
            content = "Я могу помочь с UX-дизайном, исследованиями пользователей и прототипированием."
            suggestions = [
                "UX исследования",
                "Прототипирование",
                "Дизайн системы"
            ]
        elif "проект" in prompt_lower:
            content = """Вот план работы над проектом:
- Определите целевую аудиторию
- Составьте User Stories
- Создайте CJM"""
            suggestions = [
                "Как определить аудиторию?",
                "Что такое User Stories?",
                "Как создать CJM?"
            ]
        else:
            content = "Интересный вопрос! Давай разберёмся..."
            suggestions = [
                "Узнать больше о UX",
                "Получить совет",
                "Обсудить проект"
            ]
        
        response = AgentResponse(
            content=content,
            message_type=msg_type,
            suggestions=suggestions[:3],  # Берём первые 3 suggestions
            actions=[
                {"type": "suggest", "label": "Получить совет", "payload": "advice"},
                {"type": "share", "label": "Поделиться", "payload": "share"}
            ]
        )
        
        memory.add_message("assistant", content)
        self.total_conversations += 1
        return response
