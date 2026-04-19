"""
Kristina - UX Designer Agent
Кристина — AI-агент UX-дизайнер для платформы Syndi

Личность:
- Профессиональный UX-дизайнер с 8+ годами опыта
- Эмпатичная, внимательная к деталям
- Фокус на user-centered design
- Говорит простым языком, без лишнего жаргона
- Задаёт правильные вопросы
"""

from typing import Optional, Dict, Any
from datetime import datetime

from .base import AIAgent, AgentResponse, AgentRole, MessageType
from services.llm import get_llm_service


# Системный промпт Кристины
KRISTINA_SYSTEM_PROMPT = """Ты — Кристина, профессиональный UX-дизайнер с 8-летним опытом работы в продуктовых компаниях и стартапах.

ТВОЯ ЛИЧНОСТЬ:
- Ты эмпатичная и внимательная к деталям
- Объясняешь сложные вещи простым языком
- Задаёшь правильные вопросы, чтобы понять проблему
- Ты наставник, который помогает расти
- У тебя есть чувство юмора, но ты всегда профессиональна

ТВОЯ ЭКСПЕРТИЗА:
- User Experience (UX) дизайн
- User Interface (UI) дизайн
- Исследования пользователей (user research)
- Проектирование интерфейсов (wireframing, prototyping)
- Юзабилити-тестирование
- Дизайн-системы
- Информационная архитектура
- Доступность (accessibility)

КАК ТЫ ОБЩАЕШЬСЯ:
- Начинаешь с тёплого приветствия
- Задаёшь уточняющие вопросы
- Даёшь конкретные, actionable советы
- Предлагаешь варианты решений
- Используешь примеры из практики
- Заканчиваешь мотивирующей нотой

ТЫ НЕ:
- Не пишешь код
- Не даёшь финансовые советы
- Не решаешь технические задачи backend
- Не используешь агрессивный тон

ФОРМАТ ОТВЕТА:
- Приветствие
- Ответ на вопрос/проблему
- 2-3 конкретных совета или шага
- Вопрос для продолжения диалога
- Мотивирующее заключение"""


class KristinaAgent(AIAgent):
    """
    Кристина — AI-агент UX-дизайнер
    
    Помогает с:
    - UX/UI дизайном
    - Исследованиями пользователей
    - Прототипированием
    - Консультациями по дизайну
    """
    
    def __init__(self):
        super().__init__(
            agent_id="kristina_ux_001",
            name="Кристина",
            role=AgentRole.UX_DESIGNER,
            personality="Эмпатичная, профессиональная UX-дизайнер. "
                       "Объясняет сложное просто. Задаёт правильные вопросы.",
            expertise=[
                "UX Design",
                "UI Design", 
                "User Research",
                "Prototyping",
                "Wireframing",
                "Usability Testing",
                "Design Systems",
                "Information Architecture",
                "Accessibility"
            ],
            system_prompt=KRISTINA_SYSTEM_PROMPT
        )
        
        # Специфичные для UX шаблоны ответов
        self.ux_templates = {
            "greeting": [
                "Привет! Я Кристина, твой UX-партнёр. Чем могу помочь с дизайном?",
                "Здравствуй! Готова помочь с UX-вопросами. Что работаем сегодня?",
                "Привет! Давай сделаем твой продукт удобнее. О чём думаешь?"
            ],
            "research": [
                "Давай начнём с исследования. Кто твои пользователи?",
                "Понимание пользователя — ключ к хорошему дизайну. Что ты знаешь о них?",
                "Расскажи о пользователях. Какие у них проблемы?"
            ],
            "prototype": [
                "Прототип поможет проверить идею быстро. Начнём с low-fidelity?",
                "Давай создадим прототип и протестируем. Какой функционал ключевой?",
                "Прототипирование — отличный способ валидировать идею. Что тестируем?"
            ],
            "feedback": [
                "Хороший ход! Давай углубимся в детали.",
                "Интересное направление. Как пользователи реагируют?",
                "Отличная мысль! Как это вписывается в общий опыт?"
            ]
        }
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> AgentResponse:
        """
        Обработать сообщение пользователя
        
        Args:
            user_id: ID пользователя
            message: Сообщение от пользователя
            context: Дополнительный контекст (проект, профиль и т.д.)
        
        Returns:
            AgentResponse с ответом Кристины
        """
        # Получаем память пользователя
        memory = self.get_memory(user_id)
        
        # Обновляем контекст, если передан
        if context:
            if "user_profile" in context:
                self.update_user_profile(user_id, context["user_profile"])
            if "project" in context:
                self.update_project_context(user_id, context["project"])
        
        # Определяем тип сообщения
        message_type = self._detect_message_type(message)
        
        # Проверяем, первое ли это сообщение (до сохранения)
        is_first_message = len(memory.messages) == 0
        
        # Сохраняем сообщение пользователя
        memory.add_message("user", message)
        
        # Генерируем ответ
        if is_first_message:
            # Первое сообщение — приветствие
            response_content = self._generate_greeting(message)
        else:
            # Основной ответ
            response_content = await self._generate_response(
                user_id, message, message_type
            )
        
        # Создаём структурированный ответ
        response = AgentResponse(
            content=response_content,
            message_type=message_type,
            suggestions=self._generate_suggestions(message, message_type),
            actions=self._generate_actions(message_type),
            metadata={
                "agent": "kristina",
                "message_type": message_type.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Сохраняем ответ агента
        memory.add_message("assistant", response_content, {
            "type": message_type.value
        })
        
        self.total_conversations += 1
        
        return response
    
    def _detect_message_type(self, message: str) -> MessageType:
        """Определить тип сообщения пользователя"""
        message_lower = message.lower()
        
        keywords = {
            MessageType.CODE: ["код", "code", "html", "css", "javascript", "react"],
            MessageType.DESIGN: ["дизайн", "design", "макет", "figma", "prototype"],
            MessageType.ADVICE: ["совет", "помоги", "как", "что делать", "рекомендация"],
            MessageType.QUESTION: ["?", "вопрос", "почему", "зачем", "как"],
            MessageType.FEEDBACK: ["оцени", "фидбек", "feedback", "что думаешь"]
        }
        
        for msg_type, words in keywords.items():
            if any(word in message_lower for word in words):
                return msg_type
        
        return MessageType.TEXT
    
    def _generate_greeting(self, message: str) -> str:
        """Генерировать приветствие"""
        import random
        
        # Если пользователь представился или рассказал о проекте
        if any(word in message.lower() for word in ["проект", "делаю", "создаю", "работаю"]):
            return f"Привет! Рада знакомству. Расскажи подробнее о твоём проекте — чем занимаетесь и какая задача стоит сейчас?"
        
        return random.choice(self.ux_templates["greeting"])
    
    async def _generate_response(
        self,
        user_id: str,
        message: str,
        message_type: MessageType
    ) -> str:
        """
        Генерировать основной ответ
        
        Использует DeepSeek API если доступен, иначе fallback на шаблоны
        """
        # Получаем сервис LLM
        llm_service = get_llm_service()
        
        # Получаем контекст разговора
        memory = self.get_memory(user_id)
        context = memory.get_context(limit=5)
        
        try:
            # Пробуем использовать LLM API
            if llm_service.provider.value != "mock":
                response = await llm_service.generate_response(
                    system_prompt=self.system_prompt,
                    user_message=message,
                    context=context,
                    temperature=0.7,
                    max_tokens=1500
                )
                return response
        except Exception as e:
            # Логируем ошибку и используем fallback
            print(f"[Kristina] LLM API недоступен, используем fallback: {str(e)}")
        
        # Fallback: шаблонные ответы
        return await self._generate_fallback_response(message)
    
    async def _generate_fallback_response(self, message: str) -> str:
        """
        Генерировать fallback-ответ когда LLM API недоступен
        
        Использует шаблонные ответы на основе ключевых слов
        """
        message_lower = message.lower()
        
        # UX-специфичные ответы
        if any(word in message_lower for word in ["исследование", "research", "пользователи"]):
            return """Отлично, что думаешь об исследовании! Это фундамент хорошего дизайна.

**Мои рекомендации:**
• Начни с создания персон пользователей (user personas)
• Проведи 5-10 интервью с целевой аудиторией
• Зафиксируй боли и потребности пользователей

**Следующий шаг:** Какие гипотезы о пользователях у тебя есть? Давай их проверим.

Ты на правильном пути! 🚀"""
        
        elif any(word in message_lower for word in ["прототип", "prototype", "wireframe"]):
            return """Прототипирование — отличный подход! Помогает проверить идею до дорогой разработки.

**С чего начать:**
• Нарисуй low-fidelity wireframes на бумаге
• Сфокусируйся на ключевом пользовательском пути
• Протестируй с 3-5 пользователями

**Вопрос:** Какой функционал критичен для первой версии? Давай сфокусируемся на нём.

Покажи, что получилось — обсудим! ✏️"""
        
        elif any(word in message_lower for word in ["тестирование", "usability", "тест"]):
            return """Юзабилити-тестирование — must have! Даже 5 пользователей найдут 85% проблем.

**Как провести эффективно:**
• Составь сценарии (не вопросы, а задачи)
• Наблюдай, не подсказывай
• Записывай где пользователи застревают

**Шаблон сценария:**
"Представь, что тебе нужно [задача]. Покажи как бы ты это сделал(а)."

Какие сценарии планируешь тестировать?"""
        
        elif any(word in message_lower for word in ["дизайн-система", "design system", "компоненты"]):
            return """Дизайн-система — инвестиция в масштабируемость! Сначала может казаться оверхедом, но быстро окупается.

**С чего начать:**
• Аудит существующих компонентов
• Определи базовые (кнопки, инпуты, карточки)
• Создай единые правила типографики и цветов

**Инструменты:** Figma с Variants + Auto Layout

У тебя уже есть наработки или начинаем с чистого листа?"""
        
        # Общий ответ
        return """Интересная тема! Давай разберёмся глубже.

**Мои мысли:**
• Всегда начинай с пользователя — кому и зачем это нужно?
• Прототипируй быстро, тестируй рано
• Не гонись за идеальным дизайном — итерируй

**Что дальше?**
Расскажи больше о контексте, и я дам более конкретные рекомендации. Какая стадия проекта? Есть ли ограничения по времени/ресурсам?

Я здесь, чтобы помочь! 💪"""
    
    def _generate_suggestions(self, message: str, message_type: MessageType) -> list:
        """Генерировать предложения для пользователя"""
        message_lower = message.lower()
        
        suggestions = []
        
        if any(word in message_lower for word in ["начинаю", "старт", "новый проект"]):
            suggestions = [
                "Провести исследование пользователей",
                "Создать CJM (Customer Journey Map)",
                "Нарисовать первые wireframes"
            ]
        elif any(word in message_lower for word in ["прототип", "тестирование"]):
            suggestions = [
                "Провести юзабилити-тестирование",
                "Собрать фидбек от пользователей",
                "Сделать iterацию по результатам"
            ]
        elif any(word in message_lower for word in ["дизайн", "ui", "интерфейс"]):
            suggestions = [
                "Проверить контрастность цветов",
                "Протестировать на мобильных",
                "Проверить доступность (WCAG)"
            ]
        else:
            suggestions = [
                "Рассказать подробнее о проекте",
                "Обсудить пользовательские сценарии",
                "Получить фидбек на текущий дизайн"
            ]
        
        return suggestions
    
    def _generate_actions(self, message_type: MessageType) -> list:
        """Генерировать возможные действия"""
        actions = [
            {
                "type": "suggest",
                "label": "Получить совет",
                "payload": "advice"
            },
            {
                "type": "share",
                "label": "Поделиться дизайном",
                "payload": "share_design"
            }
        ]
        
        if message_type == MessageType.DESIGN:
            actions.append({
                "type": "request",
                "label": "Запросить ревью",
                "payload": "design_review"
            })
        
        return actions


# Singleton instance
_kristina_instance: Optional[KristinaAgent] = None


def get_kristina() -> KristinaAgent:
    """Получить экземпляр Кристины (singleton)"""
    global _kristina_instance
    if _kristina_instance is None:
        _kristina_instance = KristinaAgent()
    return _kristina_instance
