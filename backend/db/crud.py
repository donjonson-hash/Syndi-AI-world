"""
CRUD Operations
"""
from typing import Optional, List
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import UserDB, BigFiveResultDB


async def create_user(db: AsyncSession, user_data: dict) -> UserDB:
    """Create new user"""
    user = UserDB(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: str) -> Optional[UserDB]:
    """Get user by ID"""
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserDB]:
    """Get user by email"""
    result = await db.execute(
        select(UserDB).where(UserDB.email == email)
    )
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[UserDB]:
    """Get list of users"""
    result = await db.execute(select(UserDB).offset(skip).limit(limit))
    return result.scalars().all()


async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """Delete user"""
    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False


async def create_big_five_result(db: AsyncSession, user_id: str, scores: dict) -> BigFiveResultDB:
    """Create Big Five test result"""
    result = BigFiveResultDB(
        user_id=user_id,
        openness=scores['openness'],
        conscientiousness=scores['conscientiousness'],
        extraversion=scores['extraversion'],
        agreeableness=scores['agreeableness'],
        neuroticism=scores['neuroticism']
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return result


async def get_big_five_result(db: AsyncSession, user_id: str) -> Optional[BigFiveResultDB]:
    """Get Big Five result for user"""
    result = await db.execute(
        select(BigFiveResultDB).where(BigFiveResultDB.user_id == user_id)
    )
    return result.scalar_one_or_none()
