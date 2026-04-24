"""
test_profile.py — GET/PATCH /api/v1/profile/me (C6).
"""
import pytest
from httpx import AsyncClient


PASSWORD = "TestPass123!"


async def _register(client: AsyncClient, email: str, name: str | None = None):
    body = {"email": email, "password": PASSWORD}
    if name:
        body["name"] = name
    resp = await client.post("/api/v1/auth/register", json=body)
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _auth_headers(client: AsyncClient, email: str, name: str | None = None):
    data = await _register(client, email, name=name)
    return {"Authorization": f"Bearer {data['token']}"}, data


# Базовый профиль онбординга для тестов (копия BUILDER из test_discover)
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


async def _onboard_for_name(client: AsyncClient, name: str):
    """Онбордит пользователя по имени (создаёт founder_profiles запись)."""
    payload = {"user_id": name, **BUILDER_RAW}
    resp = await client.post("/onboarding", json=payload)
    assert resp.status_code == 200, f"Onboard failed: {resp.text}"


# ─── GET /profile/me ─────────────────────────────────────────────────────────

class TestGetProfile:

    async def test_get_profile_no_founder_profile(self, client: AsyncClient):
        """Без founder_profile — 200, базовые данные из users."""
        headers, reg = await _auth_headers(client, "p1@test.syndi", name="Alice")
        resp = await client.get("/api/v1/profile/me", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["user_id"] == reg["id"]
        assert data["email"] == "p1@test.syndi"
        assert data["name"] == "Alice"
        # founder_profile отсутствует — id должен быть None
        assert data["id"] is None

    async def test_get_profile_with_founder_profile(self, client: AsyncClient):
        """После onboarding — 200, полные данные включая primary_role/intent_goal."""
        # Регистрируемся с name='onboarded_user', затем онбордимся с тем же user_id
        # чтобы user_id анкеты совпал с name пользователя.
        headers, reg = await _auth_headers(client, "p2@test.syndi", name="onboarded_user")
        await _onboard_for_name(client, "onboarded_user")

        resp = await client.get("/api/v1/profile/me", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["email"] == "p2@test.syndi"
        assert data["name"] == "onboarded_user"
        assert data["primary_role"] == "builder"
        assert data["intent_goal"] == "build_company"
        assert data["id"] is not None  # founder_profile UUID

    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Без токена — 401."""
        resp = await client.get("/api/v1/profile/me")
        assert resp.status_code == 401


# ─── PATCH /profile/me ───────────────────────────────────────────────────────

class TestPatchProfile:

    async def test_patch_profile_name(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "p3@test.syndi", name="OldName")
        resp = await client.patch(
            "/api/v1/profile/me",
            headers=headers,
            json={"name": "NewName"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["name"] == "NewName"

        # Перепроверим через GET
        resp2 = await client.get("/api/v1/profile/me", headers=headers)
        assert resp2.json()["name"] == "NewName"

    async def test_patch_profile_bio(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "p4@test.syndi", name="bio_user")
        await _onboard_for_name(client, "bio_user")

        resp = await client.patch(
            "/api/v1/profile/me",
            headers=headers,
            json={"bio": "Serial founder, 3 exits"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["bio"] == "Serial founder, 3 exits"

    async def test_patch_profile_unauthorized(self, client: AsyncClient):
        resp = await client.patch(
            "/api/v1/profile/me",
            json={"name": "hacker"},
        )
        assert resp.status_code == 401

    async def test_patch_creates_profile_if_missing(self, client: AsyncClient):
        """PATCH на юзера без founder_profile — создаёт запись с полями."""
        headers, _ = await _auth_headers(client, "p5@test.syndi", name="newbie")

        resp = await client.patch(
            "/api/v1/profile/me",
            headers=headers,
            json={"bio": "just starting", "primary_role": "builder"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["bio"] == "just starting"
        assert data["primary_role"] == "builder"
        assert data["id"] is not None  # founder_profile создан
