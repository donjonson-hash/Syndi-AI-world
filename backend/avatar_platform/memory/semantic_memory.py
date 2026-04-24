"""
SemanticMemory — факты о пользователе и партнёре (SQLite, без ChromaDB).
Адаптировано из kristina-revolutionary/semantic_memory.py
"""
from typing import List, Dict, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


class SemanticMemory:
    """
    Семантическая память: факты о пользователе, теги, контекст партнёрства.
    Хранится через PersistentMemory (SQLite), без векторной БД.
    """

    def __init__(self):
        self._facts: Dict[int, List[Dict]] = {}

    def add_fact(
        self,
        user_id: int,
        fact: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
    ) -> None:
        if user_id not in self._facts:
            self._facts[user_id] = []
        entry = {
            "fact": fact,
            "category": category,
            "tags": tags or [],
            "id": hashlib.md5(f"{user_id}:{fact}".encode()).hexdigest()[:12],
        }
        existing_ids = {f["id"] for f in self._facts[user_id]}
        if entry["id"] not in existing_ids:
            self._facts[user_id].append(entry)

    def get_facts(
        self,
        user_id: int,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> List[str]:
        facts = self._facts.get(user_id, [])
        if category:
            facts = [f for f in facts if f["category"] == category]
        return [f["fact"] for f in facts[-limit:]]

    def get_context_summary(self, user_id: int) -> str:
        """Краткий контекст для LLM system prompt."""
        facts = self._facts.get(user_id, [])
        if not facts:
            return ""
        items = [f["fact"] for f in facts[-5:]]
        return "Известно о пользователе: " + "; ".join(items) + "."

    def clear(self, user_id: int) -> None:
        self._facts.pop(user_id, None)
