# Agents package
from .base import AIAgent, BaseAgent, AgentResponse, AgentRole, MessageType, AgentMemory
from .kristina import KristinaUXDesigner

# Алиас для совместимости с тестами
Kristina = KristinaUXDesigner

def get_kristina():
    """Получить экземпляр агента Кристины"""
    return Kristina()

__all__ = [
    'AIAgent', 
    'BaseAgent', 
    'AgentResponse', 
    'AgentRole', 
    'MessageType',
    'AgentMemory',
    'Kristina',
    'KristinaUXDesigner',
    'get_kristina'
]
