"""
MemoryManager — фасад для трёх уровней памяти аватара.
"""
from typing import List, Dict, Tuple

from .dialog_memory import DialogMemory
from .semantic_memory import SemanticMemory
from .persistent_memory import PersistentMemory


class MemoryManager:
    """Единая точка доступа к памяти аватара."""

    def __init__(self):
        self.dialog = DialogMemory(max_messages=20)
        self.semantic = SemanticMemory()
        self.persistent = PersistentMemory()

    def build_llm_context(
        self,
        user_id: int,
        session_id: str,
        last_n: int = 8,
    ) -> Tuple[List[Dict], str]:
        """Собрать контекст для LLM: диалог + семантические факты."""
        messages = self.dialog.get_context_for_llm(session_id, last_n)
        facts_summary = self.semantic.get_context_summary(user_id)
        return messages, facts_summary
