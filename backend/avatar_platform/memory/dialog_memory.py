"""
DialogMemory — контекст текущего диалога (in-memory, последние N сообщений).
Адаптировано из kristina-revolutionary/dialog_memory.py
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class DialogMessage:
    role: str       # "user" | "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_mode: Optional[str] = None
    mood: Optional[str] = None


class DialogMemory:
    """In-memory буфер последних сообщений диалога (per session)."""

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._sessions: Dict[str, List[DialogMessage]] = {}

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_mode: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        msg = DialogMessage(role=role, content=content, agent_mode=agent_mode, mood=mood)
        self._sessions[session_id].append(msg)
        if len(self._sessions[session_id]) > self.max_messages:
            self._sessions[session_id] = self._sessions[session_id][-self.max_messages:]

    def get_messages(self, session_id: str, last_n: int = 10) -> List[Dict]:
        msgs = self._sessions.get(session_id, [])
        return [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp,
             "agent_mode": m.agent_mode, "mood": m.mood}
            for m in msgs[-last_n:]
        ]

    def get_context_for_llm(self, session_id: str, last_n: int = 8) -> List[Dict]:
        """Вернуть формат для OpenAI messages: [{"role": ..., "content": ...}]"""
        msgs = self._sessions.get(session_id, [])
        return [{"role": m.role, "content": m.content} for m in msgs[-last_n:]]

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def session_count(self) -> int:
        return len(self._sessions)
