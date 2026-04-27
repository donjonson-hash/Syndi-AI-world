"""
MessageBus — шина сообщений между аватарами со-фаундеров.
Адаптировано из kristina-revolutionary/avatar_platform/message_bus.py
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    CONTEXT_SYNC   = "context_sync"    # синхронизация контекста проекта
    TASK_ASSIGNED  = "task_assigned"   # назначена задача
    TASK_COMPLETED = "task_completed"  # задача выполнена
    STATUS_UPDATE  = "status_update"   # обновление статуса пары
    INSIGHT        = "insight"         # аватар поделился инсайтом
    ALERT          = "alert"           # предупреждение о риске


@dataclass
class BusMessage:
    msg_id: str
    from_user_id: int
    to_user_id: int
    message_type: MessageType
    payload: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    read: bool = False


class MessageBus:
    """
    In-memory шина сообщений между аватарами пары.
    Ключ: frozenset({user_a_id, user_b_id}) — симметричный канал.
    """

    _instance: Optional["MessageBus"] = None
    _channels: Dict[frozenset, List[BusMessage]] = {}
    _handlers: Dict[MessageType, List[Callable]] = {}

    @classmethod
    def get_instance(cls) -> "MessageBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _channel_key(self, user_a: int, user_b: int) -> frozenset:
        return frozenset({user_a, user_b})

    def send(
        self,
        from_user_id: int,
        to_user_id: int,
        message_type: MessageType,
        payload: Dict,
    ) -> BusMessage:
        import uuid
        msg = BusMessage(
            msg_id=str(uuid.uuid4())[:8],
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message_type=message_type,
            payload=payload,
        )
        key = self._channel_key(from_user_id, to_user_id)
        if key not in self._channels:
            self._channels[key] = []
        self._channels[key].append(msg)
        logger.info(f"MessageBus: {message_type} {from_user_id}→{to_user_id}: {payload}")
        return msg

    def get_messages(
        self,
        user_a: int,
        user_b: int,
        unread_only: bool = False,
        limit: int = 20,
    ) -> List[BusMessage]:
        key = self._channel_key(user_a, user_b)
        msgs = self._channels.get(key, [])
        if unread_only:
            msgs = [m for m in msgs if not m.read]
        return msgs[-limit:]

    def mark_read(self, user_a: int, user_b: int) -> int:
        key = self._channel_key(user_a, user_b)
        count = 0
        for msg in self._channels.get(key, []):
            if not msg.read:
                msg.read = True
                count += 1
        return count

    def get_unread_count(self, user_id: int) -> int:
        total = 0
        for key, msgs in self._channels.items():
            if user_id in key:
                total += sum(1 for m in msgs if not m.read and m.to_user_id == user_id)
        return total

    def channel_summary(self, user_a: int, user_b: int) -> Dict:
        key = self._channel_key(user_a, user_b)
        msgs = self._channels.get(key, [])
        return {
            "total_messages": len(msgs),
            "unread": sum(1 for m in msgs if not m.read),
            "last_message": msgs[-1].timestamp if msgs else None,
            "message_types": list({m.message_type for m in msgs}),
        }

    def broadcast_context_sync(
        self,
        match_id: Any,
        user_a_id: int,
        user_b_id: int,
        context: Dict,
    ) -> None:
        """Синхронизировать контекст матча между аватарами."""
        self.send(user_a_id, user_b_id, MessageType.CONTEXT_SYNC, {
            "match_id": str(match_id),
            "context": context,
            "initiator": user_a_id,
        })
        self.send(user_b_id, user_a_id, MessageType.CONTEXT_SYNC, {
            "match_id": str(match_id),
            "context": context,
            "initiator": user_a_id,
        })
