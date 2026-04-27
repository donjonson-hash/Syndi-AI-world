"""
tests/test_founder_profile_db.py — CRUD-тесты для FounderProfileDB.

Проверяют создание, получение, обновление и soft-delete профилей основателей.
"""
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.models import Base, User
from database import crud

# ── In-memory SQLite для тестов ──────────────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def db_user(db) -> User:
    """Создаёт тестового пользователя."""
    return await crud.create_user(db, {
        "name": "test_builder",
        "role": "builder",
        "skills": ["python", "fastapi"],
    })


RAW = {
    "user_id": "test_builder",
    "intent_goal": "build_product",
    "role": "builder",
    "skills": ["python", "fastapi"],
    "time_commitment": "full_time",
    "salary_readiness_months": 6,
    "launched_projects": 2,
    "sync_preference": "daily",
    "accountability_score": 85,
    "self_driven_actions": ["built_mvp"],
}

NORMALIZED = {
    "user_id": "test_builder",
    "role": "builder",
    "intent_goal": "build_product",
    "time_commitment": 100.0,
    "salary_readiness": 50.0,
    "launched_projects": 40.0,
    "sync_preference": "daily",
    "accountability": 85.0,
    "self_driven_score": 10.0,
    "skills": ["python", "fastapi"],
    "big5": None,
    "conflict_style": "collaborative",
    "decision_style": "analytical",
    "work_mode": "remote",
}


class TestFounderProfileCreate:
    async def test_create_profile(self, db, db_user):
        profile = await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        assert profile.id is not None
        assert profile.user_id == db_user.id
        assert profile.is_active is True
        assert profile.onboarding_schema_version == "syndiai-onboarding-schema-v0.1"

    async def test_raw_answers_stored(self, db, db_user):
        profile = await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        assert profile.raw_answers["user_id"] == "test_builder"
        assert profile.raw_answers["role"] == "builder"

    async def test_normalized_profile_stored(self, db, db_user):
        profile = await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        assert profile.normalized_profile["intent_goal"] == "build_product"

    async def test_upsert_updates_existing(self, db, db_user):
        """Повторный create_founder_profile обновляет запись, не создаёт дубль."""
        await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        updated_raw = {**RAW, "launched_projects": 5}
        profile = await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=updated_raw,
            normalized_profile=NORMALIZED,
        )
        assert profile.raw_answers["launched_projects"] == 5
        # Проверяем что только одна запись
        all_profiles = await crud.list_founder_profiles(db)
        assert len(all_profiles) == 1


class TestFounderProfileGet:
    async def test_get_by_user_id(self, db, db_user):
        await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        fetched = await crud.get_founder_profile_by_user_id(db, db_user.id)
        assert fetched is not None
        assert fetched.user_id == db_user.id

    async def test_get_nonexistent_returns_none(self, db):
        result = await crud.get_founder_profile_by_user_id(db, 99999)
        assert result is None

    async def test_get_by_profile_id(self, db, db_user):
        profile = await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        fetched = await crud.get_founder_profile_by_id(db, profile.id)
        assert fetched is not None
        assert fetched.id == profile.id


class TestFounderProfileList:
    async def test_list_profiles(self, db):
        user1 = await crud.create_user(db, {"name": "u1", "role": "builder"})
        user2 = await crud.create_user(db, {"name": "u2", "role": "seller"})
        await crud.create_founder_profile(db, user_id=user1.id,
                                          raw_answers=RAW, normalized_profile=NORMALIZED)
        await crud.create_founder_profile(db, user_id=user2.id,
                                          raw_answers=RAW, normalized_profile=NORMALIZED)
        profiles = await crud.list_founder_profiles(db)
        assert len(profiles) == 2

    async def test_list_profiles_exclude(self, db):
        user1 = await crud.create_user(db, {"name": "u1", "role": "builder"})
        user2 = await crud.create_user(db, {"name": "u2", "role": "seller"})
        user3 = await crud.create_user(db, {"name": "u3", "role": "operator"})
        for u in [user1, user2, user3]:
            await crud.create_founder_profile(db, user_id=u.id,
                                              raw_answers=RAW, normalized_profile=NORMALIZED)
        candidates = await crud.list_founder_profiles_exclude(db, exclude_user_id=user1.id)
        assert len(candidates) == 2
        assert all(p.user_id != user1.id for p in candidates)


class TestFounderProfileSoftDelete:
    async def test_deactivate_profile(self, db, db_user):
        await crud.create_founder_profile(
            db, user_id=db_user.id,
            raw_answers=RAW,
            normalized_profile=NORMALIZED,
        )
        result = await crud.deactivate_founder_profile(db, db_user.id)
        assert result is True
        # active_only=True не должен вернуть деактивированный профиль
        active = await crud.list_founder_profiles(db, active_only=True)
        assert len(active) == 0
        # active_only=False должен вернуть
        all_profiles = await crud.list_founder_profiles(db, active_only=False)
        assert len(all_profiles) == 1

    async def test_deactivate_nonexistent(self, db):
        result = await crud.deactivate_founder_profile(db, 99999)
        assert result is False
