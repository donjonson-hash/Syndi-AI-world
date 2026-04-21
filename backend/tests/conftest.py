"""
conftest.py — общие фикстуры для интеграционных тестов api/main.py

Использует httpx.AsyncClient с in-process ASGI transport —
реальные HTTP-запросы без поднятия сервера.
БД подменяется на SQLite in-memory чтобы тесты были изолированы.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Переключаем БД на in-memory SQLite до импорта приложения
import os
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from api.main import app, _profiles   # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def clear_profiles():
    """Очищаем in-memory профили перед каждым тестом."""
    _profiles.clear()
    yield
    _profiles.clear()


@pytest_asyncio.fixture
async def client():
    """HTTP-клиент с ASGI transport (не нужен живой сервер)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ─── Реальные профили основателей ────────────────────────────────────────────

@pytest.fixture
def profile_builder():
    """Технический сооснователь — builder, хочет строить компанию."""
    return {
        "user_id": "founder_builder",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "3+",
        "self_actions": ["built_mvp", "shipped_product", "wrote_code", "managed_team"],
        "primary_role": "builder",
        "no_go_role_tags": [],
        "decision_style": "analyze_first",
        "conflict_style": "calm_discussion",
        "work_mode": "tight_pair",
        "tempo": "iterate_fast",
        "sync_frequency": "daily",
        "accountability_disappear_label": "never",
        "accountability_ownership_label": "always",
        "big5_o_1": 4, "big5_o_2": 4,
        "big5_c_1": 5, "big5_c_2": 5, "big5_c_3": 4,
        "big5_e_1": 3, "big5_e_2": 2,
        "big5_a_1": 4, "big5_a_2": 4,
        "big5_es_1": 4, "big5_es_2": 4,
    }


@pytest.fixture
def profile_seller():
    """GTM/продажи — seller, хочет строить компанию."""
    return {
        "user_id": "founder_seller",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "1-2",
        "self_actions": ["sold_to_customers", "grew_revenue", "found_investors"],
        "primary_role": "seller",
        "no_go_role_tags": [],
        "decision_style": "fast_risky",
        "conflict_style": "calm_discussion",
        "work_mode": "tight_pair",
        "tempo": "iterate_fast",
        "sync_frequency": "daily",
        "accountability_disappear_label": "rarely",
        "accountability_ownership_label": "always",
        "big5_o_1": 4, "big5_o_2": 5,
        "big5_c_1": 4, "big5_c_2": 4, "big5_c_3": 5,
        "big5_e_1": 5, "big5_e_2": 5,
        "big5_a_1": 4, "big5_a_2": 4,
        "big5_es_1": 4, "big5_es_2": 5,
    }


@pytest.fixture
def profile_tourist():
    """Турист — хочет стабильный доход, не готов без зарплаты, слабый темп."""
    return {
        "user_id": "founder_tourist",
        "time_commitment": "part_time",
        "no_salary_readiness": "3_months",
        "intent_goal": "stable_income",
        "launched_projects": "0",
        "self_actions": [],
        "primary_role": "builder",
        "no_go_role_tags": [],
        "decision_style": "delay_until_clear",
        "conflict_style": "avoid",
        "work_mode": "solo",
        "tempo": "build_right_first",
        "sync_frequency": "weekly",
        "accountability_disappear_label": "often",
        "accountability_ownership_label": "rarely",
    }


@pytest.fixture
def profile_operator():
    """Операционный кофаундер — builder хочет строить, разный темп."""
    return {
        "user_id": "founder_operator",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "1-2",
        "self_actions": ["managed_team", "built_processes"],
        "primary_role": "operator",
        "no_go_role_tags": [],
        "decision_style": "discuss_first",
        "conflict_style": "calm_discussion",
        "work_mode": "team",
        "tempo": "build_right_first",
        "sync_frequency": "twice_a_week",
        "accountability_disappear_label": "never",
        "accountability_ownership_label": "usually",
    }


@pytest.fixture
def profile_same_role_builder():
    """Второй builder — для проверки same_primary_role флага."""
    return {
        "user_id": "founder_builder_2",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "3+",
        "self_actions": ["built_mvp", "wrote_code"],
        "primary_role": "builder",
        "no_go_role_tags": [],
        "decision_style": "analyze_first",
        "conflict_style": "calm_discussion",
        "work_mode": "tight_pair",
        "tempo": "iterate_fast",
        "sync_frequency": "daily",
        "accountability_disappear_label": "never",
        "accountability_ownership_label": "always",
    }


@pytest.fixture
def profile_volatile():
    """Нестабильный — низкий emotional_stability для high_emotional_volatility."""
    return {
        "user_id": "founder_volatile",
        "time_commitment": "full_time",
        "no_salary_readiness": "6_months",
        "intent_goal": "build_company",
        "launched_projects": "1-2",
        "self_actions": ["built_mvp"],
        "primary_role": "seller",
        "no_go_role_tags": [],
        "decision_style": "fast_risky",
        "conflict_style": "direct_clash",
        "work_mode": "solo",
        "tempo": "iterate_fast",
        "sync_frequency": "as_needed",
        "accountability_disappear_label": "always",
        "accountability_ownership_label": "never",
        # Big5: низкий emotional_stability
        "big5_o_1": 3, "big5_o_2": 3,
        "big5_c_1": 2, "big5_c_2": 2, "big5_c_3": 2,
        "big5_e_1": 2, "big5_e_2": 2,
        "big5_a_1": 2, "big5_a_2": 1,
        "big5_es_1": 1, "big5_es_2": 1,  # очень нестабильный
    }
