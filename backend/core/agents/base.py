"""
Base AI Agent Architecture
Базовая архитектура AI-агентов Syndi
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class AgentRole(str, Enum):
    """Роли агентов в экосистеме Syndi"""
    UX_DESIGNER = "ux_designer"
    DEVELOPER = "developer"
    PRODUCT_MANAGER = "product_manager"
    MARKETING = "marketing"
    MENTOR = "mentor"
    GENERAL = "general"


class MessageType(str, Enum):
    """Типы сообщений"""
    TEXT = "text"
    CODE = "code"
    DESIGN = "design"
    ADVICE = "advice"
    QUESTION = "question"
    FEEDBACK = "feedback"


@dataclass
class AgentMemory:
    """Память агента - хранит контекст разговора"""
    user_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Optional[Dict] = None
    project_context: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_interaction: datetime = field(default_factory=datetime.utcnow)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Добавить сообщение в историю"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_interaction = datetime.utcnow()
        
        # Ограничиваем историю последними 50 сообщениями
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
    
    def get_context(self, limit: int = 10) -> List[Dict]:
        """Получить последние сообщения для контекста"""
        return self.messages[-limit:]
    
    def clear(self):
        """Очистить память"""
        self.messages = []
        self.project_context = None


@dataclass
class AgentResponse:
    """Ответ агента"""
    content: str
    message_type: MessageType = MessageType.TEXT
    suggestions: List[str] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AIAgent(ABC):
    """
    Базовый класс AI-агента Syndi
    
    Все специализированные агенты наследуются от этого класса.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        personality: str,
        expertise: List[str],
        system_prompt: str
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.personality = personality
        self.expertise = expertise
        self.system_prompt = system_prompt
        
        # Хранилище памяти по пользователям
        self.memories: Dict[str, AgentMemory] = {}
        
        # Статистика
        self.total_conversations = 0
        self.created_at = datetime.utcnow()
    
    def get_memory(self, user_id: str) -> AgentMemory:
        """Получить или создать память для пользователя"""
        if user_id not in self.memories:
            self.memories[user_id] = AgentMemory(user_id=user_id)
        return self.memories[user_id]
    
    def update_user_profile(self, user_id: str, profile: Dict):
        """Обновить профиль пользователя в памяти"""
        memory = self.get_memory(user_id)
        memory.user_profile = profile
    
    def update_project_context(self, user_id: str, context: Dict):
        """Обновить контекст проекта"""
        memory = self.get_memory(user_id)
        memory.project_context = context
    
    @abstractmethod
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
            message: Сообщение пользователя
            context: Дополнительный контекст
            
        Returns:
            AgentResponse с ответом агента
        """
        pass
    
    def build_prompt(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Построить промпт для LLM
        
        Включает:
        - Системный промпт (личность агента)
        - Контекст разговора
        - Профиль пользователя
        - Контекст проекта
        """
        memory = self.get_memory(user_id)
        
        parts = [self.system_prompt]
        
        # Добавляем контекст разговора
        if memory.messages:
            parts.append("\n=== История разговора ===")
            for msg in memory.get_context(limit=5):
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                parts.append(f"{role_emoji} {msg['role']}: {msg['content'][:200]}...")
        
        # Добавляем профиль пользователя
        if memory.user_profile:
            parts.append(f"\n=== Профиль пользователя ===")
            parts.append(json.dumps(memory.user_profile, ensure_ascii=False, indent=2))
        
        # Добавляем контекст проекта
        if memory.project_context:
            parts.append(f"\n=== Контекст проекта ===")
            parts.append(json.dumps(memory.project_context, ensure_ascii=False, indent=2))
        
        # Добавляем текущее сообщение
        parts.append(f"\n=== Текущее сообщение ===")
        parts.append(f"Пользователь: {message}")
        parts.append(f"\nОтветь как {self.name}:")
        
        return "\n".join(parts)
    
    def format_response(self, raw_response: str) -> AgentResponse:
        """
        Форматировать сырой ответ LLM в структурированный AgentResponse
        
        Может быть переопределен в подклассах для специфической обработки.
        """
        # Извлекаем предложения (строки, начинающиеся с "-" или "•")
        suggestions = []
        lines = raw_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '• ', '* ')):
                suggestions.append(line[2:])
        
        return AgentResponse(
            content=raw_response,
            message_type=MessageType.TEXT,
            suggestions=suggestions[:3]  # Максимум 3 предложения
        )
    
    def get_info(self) -> Dict:
        """Получить информацию об агенте"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "expertise": self.expertise,
            "personality": self.personality,
            "total_conversations": self.total_conversations,
            "active_users": len(self.memories)
        }


class MockLLMClient:
    """
    Мок-клиент LLM для тестирования
    
    В production заменить на реальный клиент DeepSeek/Perplexity
    """
    
    def __init__(self):
        self.responses = {
            "привет": "Привет! Рада тебя видеть. Чем могу помочь сегодня?",
            "help": "Я могу помочь с UX-дизайном, исследованиями пользователей и прототипированием.",
        }
    
    async def generate(self, prompt: str) -> str:
        """Генерация ответа (мок)"""
        # В production здесь будет вызов DeepSeek/Perplexity API
        prompt_lower = prompt.lower()
        
        for key, response in self.responses.items():
            if key in prompt_lower:
                return response
        
        return "Интересный вопрос! Давай разберёмся подробнее..."


# Глобальный клиент LLM (singleton)
_llm_client: Optional[MockLLMClient] = None


def get_llm_client() -> MockLLMClient:
    """Получить клиент LLM"""
    global _llm_client
    if _llm_client is None:
        _llm_client = MockLLMClient()
    return _llm_client
