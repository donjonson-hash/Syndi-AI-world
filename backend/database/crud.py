from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, FounderProfileDB
from typing import List, Dict, Any, Optional


# ─────────────────────────────────────────────────────────────────────────────
# User CRUD
# ─────────────────────────────────────────────────────────────────────────────

async def create_user(db: AsyncSession, user_data: Dict[str, Any]) -> User:
    """
    Создаёт нового пользователя в БД.
    Перед созданием проверяй отсутствие дублей по email через get_user_by_email.
    """
    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_name(db: AsyncSession, name: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Ищет пользователя по email. Возвращает None если не найден."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int,
                      update_data: Dict[str, Any]) -> Optional[User]:
    """Обновляет поля пользователя. Возвращает обновлённый объект или None."""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    for key, value in update_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Удаляет пользователя по id. Возвращает True если удалён, False если не найден."""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True


async def get_all_candidates(db: AsyncSession, exclude_user_id: int) -> List[User]:
    """Возвращает всех активных пользователей кроме текущего."""
    result = await db.execute(
        select(User).where(
            User.id != exclude_user_id,
            User.is_active.is_(True),
        )
    )
    return result.scalars().all()


async def get_all_users(db: AsyncSession) -> List[User]:
    """Возвращает всех пользователей (для admin/debug)."""
    result = await db.execute(select(User))
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────────────────────
# Big Five results (хранится в психо-профиле User)
# ─────────────────────────────────────────────────────────────────────────────

async def create_big_five_result(db: AsyncSession, user_id: int,
                                  scores: Dict[str, Any]) -> Optional[User]:
    """Сохраняет Big Five профиль в поле psycho_profile пользователя."""
    return await update_user(db, user_id, {"psycho_profile": scores})


# ─────────────────────────────────────────────────────────────────────────────
# FounderProfile CRUD
# ─────────────────────────────────────────────────────────────────────────────

async def create_founder_profile(
    db: AsyncSession,
    user_id: int,
    raw_answers: Dict[str, Any],
    normalized_profile: Dict[str, Any],
    schema_version: str = "syndiai-onboarding-schema-v0.1",
) -> FounderProfileDB:
    """Создаёт запись founder_profiles. Если для user_id уже есть — обновляет."""
    existing = await get_founder_profile_by_user_id(db, user_id)
    if existing:
        existing.raw_answers = raw_answers
        existing.normalized_profile = normalized_profile
        existing.onboarding_schema_version = schema_version
        await db.commit()
        await db.refresh(existing)
        return existing

    record = FounderProfileDB(
        user_id=user_id,
        raw_answers=raw_answers,
        normalized_profile=normalized_profile,
        onboarding_schema_version=schema_version,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_founder_profile_by_user_id(
    db: AsyncSession, user_id: int
) -> Optional[FounderProfileDB]:
    """Возвращает FounderProfileDB по user_id или None."""
    result = await db.execute(
        select(FounderProfileDB).where(FounderProfileDB.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_founder_profile_by_id(
    db: AsyncSession, profile_id: str
) -> Optional[FounderProfileDB]:
    """Возвращает FounderProfileDB по UUID или None."""
    result = await db.execute(
        select(FounderProfileDB).where(FounderProfileDB.id == profile_id)
    )
    return result.scalar_one_or_none()


async def list_founder_profiles(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
    active_only: bool = True,
) -> List[FounderProfileDB]:
    """Список всех профилей. active_only=True возвращает только is_active=True."""
    query = select(FounderProfileDB)
    if active_only:
        query = query.where(FounderProfileDB.is_active.is_(True))
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def list_founder_profiles_exclude(
    db: AsyncSession,
    exclude_user_id: int,
    limit: int = 100,
) -> List[FounderProfileDB]:
    """Все активные профили кроме указанного user_id — для матчинга."""
    result = await db.execute(
        select(FounderProfileDB)
        .where(
            FounderProfileDB.user_id != exclude_user_id,
            FounderProfileDB.is_active.is_(True),
        )
        .limit(limit)
    )
    return result.scalars().all()


async def deactivate_founder_profile(
    db: AsyncSession, user_id: int
) -> bool:
    """Помечает профиль как неактивный (soft delete)."""
    record = await get_founder_profile_by_user_id(db, user_id)
    if not record:
        return False
    record.is_active = False
    await db.commit()
    return True
