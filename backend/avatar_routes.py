"""Avatar endpoints — получение и управление AI-аватарами со-фаундеров."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user
from database.models import User as UserDB
from avatar_platform.avatar_factory import AvatarFactory
from avatar_platform.message_bus import MessageBus, MessageType

router = APIRouter(prefix="/api/v1/avatar", tags=["avatar"])


@router.get("/me")
async def get_my_avatar(current_user: UserDB = Depends(get_current_user)):
    """Получить AI-аватар текущего пользователя."""
    avatar = AvatarFactory.get_avatar(current_user.id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found. Complete a match first.")
    return avatar.to_dict()


@router.get("/list")
async def list_avatars(current_user: UserDB = Depends(get_current_user)):
    """Список всех аватаров (admin/debug)."""
    return {"avatars": AvatarFactory.list_avatars(), "total": len(AvatarFactory._avatars)}


# ─── E2: MessageBus endpoints ─────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    to_user_id: int
    message_type: str
    payload: dict


class MarkReadRequest(BaseModel):
    partner_user_id: int


def _msg_to_dict(m) -> dict:
    return {
        "msg_id": m.msg_id,
        "from_user_id": m.from_user_id,
        "to_user_id": m.to_user_id,
        "message_type": m.message_type.value if hasattr(m.message_type, "value") else m.message_type,
        "payload": m.payload,
        "timestamp": m.timestamp,
        "read": m.read,
    }


@router.get("/messages")
async def get_avatar_messages(
    partner_user_id: int,
    unread_only: bool = False,
    current_user: UserDB = Depends(get_current_user),
):
    """Получить сообщения между аватарами текущего юзера и партнёра."""
    bus = MessageBus.get_instance()
    msgs = bus.get_messages(current_user.id, partner_user_id, unread_only=unread_only)
    summary = bus.channel_summary(current_user.id, partner_user_id)
    return {
        "messages": [_msg_to_dict(m) for m in msgs],
        "total": summary["total_messages"],
        "unread_count": summary["unread"],
    }


@router.post("/messages")
async def send_avatar_message(
    body: SendMessageRequest,
    current_user: UserDB = Depends(get_current_user),
):
    """Отправить сообщение от своего аватара партнёру."""
    try:
        mtype = MessageType(body.message_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown message_type: {body.message_type}")
    bus = MessageBus.get_instance()
    msg = bus.send(
        from_user_id=current_user.id,
        to_user_id=body.to_user_id,
        message_type=mtype,
        payload=body.payload,
    )
    return {"msg_id": msg.msg_id, "sent": True}


@router.post("/messages/read")
async def mark_messages_read(
    body: MarkReadRequest,
    current_user: UserDB = Depends(get_current_user),
):
    """Отметить все сообщения в канале с партнёром как прочитанные."""
    bus = MessageBus.get_instance()
    count = bus.mark_read(current_user.id, body.partner_user_id)
    return {"marked_read": count}


@router.get("/channel")
async def get_channel_summary(
    partner_user_id: int,
    current_user: UserDB = Depends(get_current_user),
):
    """Сводка по каналу с партнёром."""
    bus = MessageBus.get_instance()
    return bus.channel_summary(current_user.id, partner_user_id)
