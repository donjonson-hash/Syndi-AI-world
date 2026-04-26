from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Message, Conversation, User
from ..schemas import MessageCreate, MessageOut, ConversationOut
from ..routers.auth import get_current_user

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationOut])
async def conversations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    convs = (await db.execute(select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.last_message_at.desc()))).scalars().all()
    out = []
    for c in convs:
        p = (await db.execute(select(User).where(User.id == c.partner_id))).scalar_one_or_none()
        out.append(ConversationOut(id=str(c.id), partner_id=str(c.partner_id), partner_name=p.name if p else "Unknown",
                                    partner_avatar=p.avatar_url if p else None, last_message=c.last_message,
                                    last_message_at=c.last_message_at, unread_count=c.unread_count))
    return out

@router.get("/{partner_id}", response_model=List[MessageOut])
async def messages(partner_id: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    msgs = (await db.execute(
        select(Message).where(or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == partner_id),
            and_(Message.sender_id == partner_id, Message.receiver_id == current_user.id),
        )).order_by(Message.created_at.desc()).offset(skip).limit(limit)
    )).scalars().all()
    return [MessageOut(id=str(m.id), sender_id=str(m.sender_id), receiver_id=str(m.receiver_id),
                        text=m.text, is_ai_suggestion=bool(m.is_ai_suggestion), created_at=m.created_at) for m in msgs]

@router.post("/", response_model=MessageOut)
async def send(data: MessageCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = Message(sender_id=current_user.id, receiver_id=data.receiver_id, text=data.text)
    db.add(msg)
    # Update conversations
    for uid, pid in [(current_user.id, data.receiver_id), (data.receiver_id, current_user.id)]:
        c = (await db.execute(select(Conversation).where(and_(Conversation.user_id == uid, Conversation.partner_id == pid)))).scalar_one_or_none()
        if c:
            c.last_message, c.last_message_at = data.text, datetime.utcnow()
            c.unread_count = 0 if uid == current_user.id else c.unread_count + 1
        else:
            db.add(Conversation(user_id=uid, partner_id=pid, last_message=data.text, last_message_at=datetime.utcnow(), unread_count=0 if uid == current_user.id else 1))
    await db.commit()
    await db.refresh(msg)
    return MessageOut(id=str(msg.id), sender_id=str(msg.sender_id), receiver_id=str(msg.receiver_id),
                      text=msg.text, is_ai_suggestion=bool(msg.is_ai_suggestion), created_at=msg.created_at)
