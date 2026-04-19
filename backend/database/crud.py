from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User
from typing import List, Dict, Any

async def create_user(db: AsyncSession, user_data: Dict[str, Any]) -> User:
    """
    Создает нового пользователя в БД.
    user_data должен соответствовать полям модели User.
    """
    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_all_candidates(db: AsyncSession, exclude_user_id: int) -> List[User]:
    """
    Достает всех пользователей, кроме текущего (чтобы не мэтчить самого с собой).
    """
    result = await db.execute(
        select(User).where(User.id != exclude_user_id)
    )
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_name(db: AsyncSession, name: str) -> User:
    result = await db.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()

