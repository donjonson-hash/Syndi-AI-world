"""
test_db_compat.py — unit тесты совместимости БД и Redis (D7).

Проверяем:
  - DATABASE_URL дефолт → SQLite
  - DATABASE_URL env var → PostgreSQL engine использует asyncpg
  - Redis graceful degradation: без сервера cache_* не падает, возвращает
    None/False, а discover-роут отвечает 200.

Тесты SQLite-only — настоящего PostgreSQL не требуется.
"""
import importlib
import sys

import pytest_asyncio
from httpx import AsyncClient


# ─── 1. DATABASE_URL ─────────────────────────────────────────────────────────

def test_database_url_sqlite_default(monkeypatch):
    """Без DATABASE_URL → движок строится на SQLite."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    sys.modules.pop("database.database", None)
    mod = importlib.import_module("database.database")
    try:
        assert mod.DATABASE_URL.startswith("sqlite")
        assert mod.engine.dialect.name == "sqlite"
    finally:
        # Возвращаем тестовое окружение
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        sys.modules.pop("database.database", None)
        importlib.import_module("database.database")


def test_database_url_postgres_from_env(monkeypatch):
    """Если DATABASE_URL начинается с postgresql+asyncpg:// — используется asyncpg."""
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://syndi:syndi@localhost:5432/syndi_db",
    )
    sys.modules.pop("database.database", None)
    mod = importlib.import_module("database.database")
    try:
        assert mod.DATABASE_URL.startswith("postgresql+asyncpg://")
        assert mod.engine.dialect.name == "postgresql"
        # asyncpg driver
        assert "asyncpg" in str(mod.engine.url).lower()
    finally:
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        sys.modules.pop("database.database", None)
        importlib.import_module("database.database")


# ─── 2. Redis graceful degradation ───────────────────────────────────────────

@pytest_asyncio.fixture
async def unavailable_redis(monkeypatch):
    """Подменяет REDIS_URL на гарантированно недоступный порт и сбрасывает клиент."""
    # Порт 1 обычно закрыт/занят и даёт ConnectionRefused быстро
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")
    from database import redis_client
    # Сброс кэшированного клиента
    await redis_client.close_redis()
    redis_client.REDIS_URL = "redis://127.0.0.1:1/0"
    yield redis_client
    await redis_client.close_redis()


async def test_redis_client_graceful_without_server(unavailable_redis):
    """get_redis() без Redis → возвращает None, не падает."""
    client = await unavailable_redis.get_redis()
    assert client is None


async def test_cache_set_without_redis(unavailable_redis):
    """cache_set без Redis → возвращает False, не падает."""
    ok = await unavailable_redis.cache_set("test_key", {"foo": "bar"}, ttl=60)
    assert ok is False


async def test_cache_get_without_redis(unavailable_redis):
    """cache_get без Redis → возвращает None, не падает."""
    val = await unavailable_redis.cache_get("test_key")
    assert val is None


async def test_cache_delete_without_redis(unavailable_redis):
    """cache_delete без Redis → возвращает False, не падает."""
    ok = await unavailable_redis.cache_delete("test_key")
    assert ok is False


# ─── 3. Discover route works without Redis ───────────────────────────────────

BUILDER_PROFILE = {
    "user_id": "compat_builder",
    "time_commitment": "full_time", "no_salary_readiness": "12_months",
    "intent_goal": "build_company", "launched_projects": "3+",
    "self_actions": ["built_mvp", "wrote_code"],
    "primary_role": "builder", "no_go_role_tags": [],
    "decision_style": "analyze_first", "conflict_style": "calm_discussion",
    "work_mode": "tight_pair", "tempo": "iterate_fast",
    "sync_frequency": "daily",
    "accountability_disappear_label": "never",
    "accountability_ownership_label": "always",
}

SELLER_PROFILE = {
    "user_id": "compat_seller",
    "time_commitment": "full_time", "no_salary_readiness": "12_months",
    "intent_goal": "build_company", "launched_projects": "1-2",
    "self_actions": ["sold_to_customers", "grew_revenue"],
    "primary_role": "seller", "no_go_role_tags": [],
    "decision_style": "fast_risky", "conflict_style": "calm_discussion",
    "work_mode": "tight_pair", "tempo": "iterate_fast",
    "sync_frequency": "daily",
    "accountability_disappear_label": "rarely",
    "accountability_ownership_label": "always",
}


async def test_discover_route_works_without_redis(client: AsyncClient, monkeypatch):
    """GET /api/v1/discover с токеном → 200 даже если Redis недоступен (graceful)."""
    # Forcibly break Redis for этот тест
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")
    from database import redis_client
    await redis_client.close_redis()
    redis_client.REDIS_URL = "redis://127.0.0.1:1/0"

    try:
        # Регистрируем пользователя для JWT
        auth = await client.post("/api/v1/auth/register", json={
            "email": "compat_disc@test.syndi", "password": "TestPass123!",
        })
        assert auth.status_code == 200
        token = auth.json()["token"]
        client.headers["Authorization"] = f"Bearer {token}"

        # Онбординг двух профилей
        r1 = await client.post("/onboarding", json=BUILDER_PROFILE)
        assert r1.status_code == 200
        r2 = await client.post("/onboarding", json=SELLER_PROFILE)
        assert r2.status_code == 200

        users = (await client.get("/users")).json()
        uid_map = {u["name"]: u["id"] for u in users}
        builder_uid = uid_map["compat_builder"]

        resp = await client.get(f"/api/v1/discover?user_id={builder_uid}")
        assert resp.status_code == 200, f"Discover should work without Redis: {resp.text}"
        data = resp.json()
        assert "cards" in data
    finally:
        client.headers.pop("Authorization", None)
        await redis_client.close_redis()
