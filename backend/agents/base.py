"""
Base AI Agent Architecture
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AgentRole(str, Enum):
    UX_DESIGNER = "ux_designer"
    DEVELOPER = "developer"
    PRODUCT_MANAGER = "product_manager"
    MARKETING = "marketing"
    MENTOR = "mentor"
    GENERAL = "general"


class MessageType(str, Enum):
    TEXT = "text"
    CODE = "code"
    DESIGN = "design"
    ADVICE = "advice"
    QUESTION = "question"
    FEEDBACK = "feedback"


@dataclass
class AgentMemory:
    user_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Optional[Dict] = None
    project_context: Optional[Dict] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_interaction: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_interaction = datetime.now(timezone.utc)
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
    
    def get_context(self, limit: int = 10) -> List[Dict]:
        return self.messages[-limit:]
    
    def clear(self):
        self.messages = []
        self.project_context = None


@dataclass
class AgentResponse:
    content: str
    message_type: MessageType = MessageType.TEXT
    suggestions: List[str] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AIAgent(ABC):
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
        self.memories: Dict[str, AgentMemory] = {}
        self.total_conversations = 0
        self.created_at = datetime.now(timezone.utc)
    
    def get_memory(self, user_id: str) -> AgentMemory:
        if user_id not in self.memories:
            self.memories[user_id] = AgentMemory(user_id=user_id)
        return self.memories[user_id]
    
    def update_user_profile(self, user_id: str, profile: Dict):
        """NEW: Update user profile"""
        memory = self.get_memory(user_id)
        memory.user_profile = profile
    
    def update_project_context(self, user_id: str, context: Dict):
        """NEW: Update project context"""
        memory = self.get_memory(user_id)
        memory.project_context = context
    
    @abstractmethod
    async def process_message(self, user_id: str, message: str, context: Optional[Dict] = None) -> AgentResponse:
        pass
    
    def get_info(self) -> Dict:
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
    def __init__(self):
        self.responses = {
            "привет": "Привет! Рада тебя видеть.",
            "help": "Я могу помочь с UX-дизайном.",
            "исследование": "Исследование пользователей — ключевой этап UX.",
            "прототип": "Прототипирование помогает проверить идеи.",
            "проект": "- Определите аудиторию\n- Составьте User Stories",
        }
    
    async def generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for key, response in self.responses.items():
            if key in prompt_lower:
                return response
        return "Интересный вопрос!"


_llm_client: Optional[MockLLMClient] = None

def get_llm_client() -> MockLLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = MockLLMClient()
    return _llm_client

# Алиас для совместимости

# Алиас для совместимости с тестами

# Алиас для совместимости с тестами
BaseAgent = AIAgent


# Алиас для совместимости с тестами
BaseAgent = AIAgent

