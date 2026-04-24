from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from database.models import User, FounderProfileDB
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────────────────
# User CRUD
# ─────────────────────────────────────────────────────────────────────────────

async def create_user(db: AsyncSession, user_data: Dict[str, Any]) -> User:
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
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int,
                      update_data: Dict[str, Any]) -> Optional[User]:
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
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True


async def get_all_candidates(db: AsyncSession, exclude_user_id: int) -> List[User]:
    result = await db.execute(
        select(User).where(
            User.id != exclude_user_id,
            User.is_active.is_(True),
        )
    )
    return result.scalars().all()


async def get_all_users(db: AsyncSession) -> List[User]:
    result = await db.execute(select(User))
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────────────────────
# Big Five
# ─────────────────────────────────────────────────────────────────────────────

async def create_big_five_result(db: AsyncSession, user_id: int,
                                  scores: Dict[str, Any]) -> Optional[User]:
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
    result = await db.execute(
        select(FounderProfileDB).where(FounderProfileDB.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_founder_profile_by_id(
    db: AsyncSession, profile_id: str
) -> Optional[FounderProfileDB]:
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
    record = await get_founder_profile_by_user_id(db, user_id)
    if not record:
        return False
    record.is_active = False
    await db.commit()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Like CRUD  [v0.2]
# ─────────────────────────────────────────────────────────────────────────────

async def create_or_update_like(
    db: AsyncSession,
    from_user_id: int,
    to_user_id: int,
    is_like: bool,
) -> "LikeDB":
    """Создаёт или обновляет лайк/дизлайк from → to."""
    from database.models import LikeDB

    existing = await get_like(db, from_user_id, to_user_id)
    if existing:
        existing.is_like = is_like
        await db.commit()
        await db.refresh(existing)
        return existing

    record = LikeDB(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        is_like=is_like,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_like(
    db: AsyncSession,
    from_user_id: int,
    to_user_id: int,
) -> Optional["LikeDB"]:
    """Возвращает LikeDB для пары from→to или None."""
    from database.models import LikeDB
    result = await db.execute(
        select(LikeDB).where(
            LikeDB.from_user_id == from_user_id,
            LikeDB.to_user_id == to_user_id,
        )
    )
    return result.scalar_one_or_none()


async def check_mutual_like(
    db: AsyncSession,
    user_a_id: int,
    user_b_id: int,
) -> bool:
    """True если оба поставили is_like=True друг другу."""
    like_ab = await get_like(db, user_a_id, user_b_id)
    like_ba = await get_like(db, user_b_id, user_a_id)
    return bool(like_ab and like_ab.is_like and like_ba and like_ba.is_like)


# ─────────────────────────────────────────────────────────────────────────────
# Match CRUD  [v0.2]
# ─────────────────────────────────────────────────────────────────────────────

async def create_match(
    db: AsyncSession,
    user_a_id: int,
    user_b_id: int,
    match_score: Optional[float] = None,
) -> "MatchDB":
    """Создаёт match (idempotent — возвращает существующий если уже есть)."""
    from database.models import MatchDB

    # Нормализуем порядок — меньший id всегда user_a
    a, b = (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)

    existing = await get_match(db, a, b)
    if existing:
        return existing

    record = MatchDB(
        user_a_id=a,
        user_b_id=b,
        match_score=match_score,
        status="active",
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_match(
    db: AsyncSession,
    user_a_id: int,
    user_b_id: int,
) -> Optional["MatchDB"]:
    """Ищет match по паре (порядок не важен)."""
    from database.models import MatchDB
    a, b = (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)
    result = await db.execute(
        select(MatchDB).where(
            MatchDB.user_a_id == a,
            MatchDB.user_b_id == b,
        )
    )
    return result.scalar_one_or_none()


async def list_matches_for_user(
    db: AsyncSession,
    user_id: int,
    active_only: bool = True,
) -> List["MatchDB"]:
    """Все матчи пользователя (как user_a или user_b)."""
    from database.models import MatchDB
    query = select(MatchDB).where(
        or_(MatchDB.user_a_id == user_id, MatchDB.user_b_id == user_id)
    )
    if active_only:
        query = query.where(MatchDB.status == "active")
    result = await db.execute(query)
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────────────────────
# Profile updates (C6)
# ─────────────────────────────────────────────────────────────────────────────

async def update_founder_profile(
    db: AsyncSession,
    user_id: int,
    updates: Dict[str, Any],
) -> FounderProfileDB:
    """Обновляет поля внутри normalized_profile для founder_profiles.
    Если записи нет — создаёт минимальную с этими полями."""
    record = await get_founder_profile_by_user_id(db, user_id)
    if record is None:
        record = FounderProfileDB(
            user_id=user_id,
            raw_answers={},
            normalized_profile=dict(updates),
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    np = dict(record.normalized_profile or {})
    np.update(updates)
    record.normalized_profile = np
    await db.commit()
    await db.refresh(record)
    return record
