"""
API Routes для Kristina AI Agent (C7).

POST /api/v1/kristina/chat   — JWT-protected: диалог с Кристиной
GET  /api/v1/kristina/status — публичный: статус агента и доступность LLM
GET  /api/v1/kristina/history — JWT-protected: история сообщений пользователя
"""
import os
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from agents.kristina import KristinaUXDesigner
from auth import get_current_user
from database.database import get_db
from database.models import User as UserDB


router = APIRouter(prefix="/api/v1/kristina", tags=["kristina"])


kristina = KristinaUXDesigner()


FALLBACK_REPLY = (
    "Привет! Я Кристина. Расскажи о своём проекте — "
    "я помогу найти идеального со-фаундера."
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    agent: str = "kristina"
    session_id: str
    suggestions: List[str] = []
    message_type: str = "text"
    mood: Optional[str] = None  # mood_description из EmotionalCore
    mode: Optional[str] = None  # "advisor" | "mentor" | "executor"


class StatusResponse(BaseModel):
    status: str
    agent: str
    version: str
    llm_available: bool


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    total: int


def _llm_available() -> bool:
    key = os.getenv("MIMO_API_KEY", "")
    return bool(key and key.strip())


@router.get("/status", response_model=StatusResponse)
async def kristina_status():
    return StatusResponse(
        status="active",
        agent="kristina",
        version="2.0",
        llm_available=_llm_available(),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_kristina(
    payload: ChatRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session_id = payload.session_id or str(current_user.id)

    mood: Optional[str] = None
    mode: Optional[str] = None
    try:
        agent_resp = await kristina.process_message(session_id, payload.message)
        content = agent_resp.content
        suggestions = list(agent_resp.suggestions or [])
        msg_type = (
            agent_resp.message_type.value
            if hasattr(agent_resp.message_type, "value")
            else str(agent_resp.message_type)
        )
        if agent_resp.metadata:
            mood = agent_resp.metadata.get("mood_description")
            mode = agent_resp.metadata.get("mode")
        if not isinstance(content, str) or not content.strip():
            content = FALLBACK_REPLY
    except Exception:
        content = FALLBACK_REPLY
        suggestions = []
        msg_type = "text"

    # Сохраняем в PersistentMemory — не роняем чат при ошибке БД.
    try:
        await kristina.memory_manager.persistent.save_message(
            db, current_user.id, session_id,
            role="user", content=payload.message,
            memory_type="dialog", agent_mode=mode,
        )
        await kristina.memory_manager.persistent.save_message(
            db, current_user.id, session_id,
            role="assistant", content=content,
            memory_type="dialog", agent_mode=mode, mood=mood,
        )
    except Exception:
        pass

    return ChatResponse(
        response=content,
        agent="kristina",
        session_id=session_id,
        suggestions=suggestions,
        message_type=msg_type,
        mood=mood,
        mode=mode,
    )


@router.get("/history", response_model=HistoryResponse)
async def kristina_history(
    session_id: Optional[str] = None,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sid = session_id or str(current_user.id)

    # Если есть записи в PersistentMemory — возвращаем из БД.
    try:
        db_rows = await kristina.memory_manager.persistent.get_history(
            db, current_user.id, session_id=sid, limit=50,
        )
    except Exception:
        db_rows = []

    if db_rows:
        return HistoryResponse(
            session_id=sid,
            messages=db_rows,
            total=len(db_rows),
        )

    memory = kristina.get_memory(sid)
    messages = list(memory.messages)
    return HistoryResponse(
        session_id=sid,
        messages=messages,
        total=len(messages),
    )