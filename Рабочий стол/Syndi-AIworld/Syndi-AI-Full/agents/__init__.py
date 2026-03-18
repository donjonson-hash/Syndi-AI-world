"""
AI Agents Module for Syndi
Модуль персональных AI-агентов платформы Syndi
"""

from .base import AIAgent, AgentResponse, AgentMemory
from .kristina import KristinaAgent, get_kristina

__all__ = [
    "AIAgent",
    "AgentResponse", 
    "AgentMemory",
    "KristinaAgent",
    "get_kristina"
]
