"""
test_jwt_protection.py — проверяем что like/match/discover требуют Bearer-токен.

Без токена или с невалидным токеном эндпоинты должны возвращать 401.
С валидным токеном — работать штатно.
"""
import pytest
from httpx import AsyncClient


BUILDER_PROFILE = {
    "user_id": "jwt_prot_builder",
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
    "user_id": "jwt_prot_seller",
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


async def _register_and_token(client: AsyncClient, email: str) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "JwtProtPass123!"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


# ─── Без токена → 401 ────────────────────────────────────────────────────────

class TestWithoutToken:

    async def test_like_without_token(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/like/1",
            json={"from_user_id": 1, "is_like": True},
        )
        assert resp.status_code == 401

    async def test_matches_without_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/matches?user_id=1")
        assert resp.status_code == 401

    async def test_discover_without_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/discover?user_id=1")
        assert resp.status_code == 401


# ─── Невалидный токен → 401 ───────────────────────────────────────────────────

class TestInvalidToken:

    async def test_like_with_invalid_token(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/like/1",
            json={"from_user_id": 1, "is_like": True},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    async def test_matches_with_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/matches?user_id=1",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    async def test_discover_with_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/discover?user_id=1",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


# ─── Валидный токен → 200 ─────────────────────────────────────────────────────

class TestValidToken:

    async def test_discover_with_valid_token(self, client: AsyncClient):
        """С валидным токеном /discover отрабатывает (200) для пользователя с профилем."""
        token = await _register_and_token(client, "jwt_prot_valid@test.syndi")
        headers = {"Authorization": f"Bearer {token}"}

        # Онбординг: создаёт user + founder_profile и нужен кандидат для ленты
        ob1 = await client.post("/onboarding", json=BUILDER_PROFILE)
        ob2 = await client.post("/onboarding", json=SELLER_PROFILE)
        assert ob1.status_code == 200, ob1.text
        assert ob2.status_code == 200, ob2.text

        users = (await client.get("/users")).json()
        uid_map = {u["name"]: u["id"] for u in (users if isinstance(users, list) else [])}
        builder_uid = uid_map["jwt_prot_builder"]

        resp = await client.get(
            f"/api/v1/discover?user_id={builder_uid}",
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "cards" in data

    async def test_like_with_valid_token(self, client: AsyncClient):
        """С валидным токеном /like отрабатывает (200)."""
        token = await _register_and_token(client, "jwt_prot_like@test.syndi")
        headers = {"Authorization": f"Bearer {token}"}

        u1 = (await client.post("/users", json={
            "name": "jwt_like_u1", "email": "jwt_like_u1@test.syndi", "role": "builder",
        })).json()
        u2 = (await client.post("/users", json={
            "name": "jwt_like_u2", "email": "jwt_like_u2@test.syndi", "role": "seller",
        })).json()

        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
