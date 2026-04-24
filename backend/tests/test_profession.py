"""
test_profession.py — ProfessionProfile + PROFESSION_REGISTRY (D1).
"""
import pytest
from httpx import AsyncClient

from avatar_platform.profession_profile import (
    PROFESSION_REGISTRY,
    ProfessionProfile,
    get_profession,
)


PASSWORD = "TestPass123!"


BUILDER_RAW = {
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


# ─── Unit-тесты реестра ──────────────────────────────────────────────────────

def test_registry_has_all_roles():
    for role in ("builder", "seller", "operator", "researcher"):
        assert role in PROFESSION_REGISTRY
        assert isinstance(PROFESSION_REGISTRY[role], ProfessionProfile)


def test_builder_has_skills():
    b = get_profession("builder")
    assert b is not None
    assert len(b.core_skills) > 0


def test_build_system_prompt():
    p = get_profession("seller")
    assert p is not None
    prompt = p.build_system_prompt("Иван")
    assert isinstance(prompt, str)
    assert "Иван" in prompt
    assert p.title in prompt


def test_get_profession_unknown():
    assert get_profession("unknown") is None


def test_all_roles_have_routine_tasks():
    for role_id, profile in PROFESSION_REGISTRY.items():
        assert profile.routine_tasks, f"{role_id} must have routine_tasks"


# ─── Интеграционный тест с /profile/me ───────────────────────────────────────

async def test_profession_profile_in_get_profile(client: AsyncClient):
    """GET /api/v1/profile/me после онбординга содержит поле profession."""
    # Регистрируем пользователя с name, совпадающим с user_id анкеты
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "prof@test.syndi", "password": PASSWORD, "name": "prof_user"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Онбордим с primary_role=builder
    onboard_resp = await client.post(
        "/onboarding",
        json={"user_id": "prof_user", **BUILDER_RAW},
    )
    assert onboard_resp.status_code == 200, onboard_resp.text

    # GET /profile/me → должен включать profession
    resp = await client.get("/api/v1/profile/me", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["primary_role"] == "builder"
    assert data["profession"] is not None
    assert "title" in data["profession"]
    assert "core_skills" in data["profession"]
    assert "routine_tasks" in data["profession"]
    assert len(data["profession"]["core_skills"]) > 0
