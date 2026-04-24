"""
PersistentMemory — долгосрочное хранилище в SQLite через SQLAlchemy async.
Адаптировано из kristina-revolutionary/persistent_memory.py
"""
from typing import List, Dict, Optional
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

logger = logging.getLogger(__name__)


class PersistentMemory:
    """Сохраняет сообщения в avatar_memories таблицу."""

    async def save_message(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: str,
        role: str,
        content: str,
        memory_type: str = "dialog",
        agent_mode: Optional[str] = None,
        mood: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        try:
            from database.models import AvatarMemoryDB
            entry = AvatarMemoryDB(
                user_id=user_id,
                session_id=session_id,
                memory_type=memory_type,
                role=role,
                content=content,
                tags=json.dumps(tags or []),
                agent_mode=agent_mode,
                mood=mood,
            )
            db.add(entry)
            await db.commit()
            return True
        except Exception as e:
            logger.warning(f"PersistentMemory save error: {e}")
            try:
                await db.rollback()
            except Exception:
                pass
            return False

    async def get_history(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: Optional[str] = None,
        limit: int = 20,
        memory_type: Optional[str] = None,
    ) -> List[Dict]:
        try:
            from database.models import AvatarMemoryDB
            q = select(AvatarMemoryDB).where(AvatarMemoryDB.user_id == user_id)
            if session_id:
                q = q.where(AvatarMemoryDB.session_id == session_id)
            if memory_type:
                q = q.where(AvatarMemoryDB.memory_type == memory_type)
            q = q.order_by(desc(AvatarMemoryDB.created_at), desc(AvatarMemoryDB.id)).limit(limit)
            result = await db.execute(q)
            rows = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "role": r.role,
                    "content": r.content,
                    "memory_type": r.memory_type,
                    "agent_mode": r.agent_mode,
                    "mood": r.mood,
                    "tags": json.loads(r.tags or "[]"),
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reversed(rows)
            ]
        except Exception as e:
            logger.warning(f"PersistentMemory get error: {e}")
            return []
