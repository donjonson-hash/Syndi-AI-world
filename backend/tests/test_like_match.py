"""
test_like_match.py — интеграционные тесты для like/match механики.

POST /api/v1/like/{to_user_id}
GET  /api/v1/matches?user_id={id}
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

BUILDER_PROFILE = {
    "user_id": "like_test_builder",
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

SELLER_PROFILE = {
    "user_id": "like_test_seller",
    "time_commitment": "full_time",
    "no_salary_readiness": "12_months",
    "intent_goal": "build_company",
    "launched_projects": "1-2",
    "self_actions": ["sold_to_customers", "grew_revenue"],
    "primary_role": "seller",
    "no_go_role_tags": [],
    "decision_style": "fast_risky",
    "conflict_style": "calm_discussion",
    "work_mode": "tight_pair",
    "tempo": "iterate_fast",
    "sync_frequency": "daily",
    "accountability_disappear_label": "rarely",
    "accountability_ownership_label": "always",
}


async def _onboard(client: AsyncClient, profile: dict) -> dict:
    """Онбордит профиль и возвращает ответ."""
    resp = await client.post("/onboarding", json=profile)
    assert resp.status_code == 200, f"Onboard failed: {resp.text}"
    return resp.json()


async def _get_user_id(client: AsyncClient, name: str) -> int:
    """Получает integer user_id по имени через /users."""
    resp = await client.get(f"/users?name={name}")
    # fallback: ищем через создание пользователя повторно — берём из onboard ответа
    # В тестах используем специальный endpoint или напрямую через DB
    # Здесь просто онбордим и ищем в /users
    users_resp = await client.get("/users")
    if users_resp.status_code == 200:
        users = users_resp.json()
        if isinstance(users, list):
            for u in users:
                if u.get("name") == name:
                    return u["id"]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Test Classes
# ─────────────────────────────────────────────────────────────────────────────

class TestLikeEndpoint:
    """POST /api/v1/like/{to_user_id}"""

    async def test_like_returns_200(self, client: AsyncClient):
        """Лайк существующего пользователя возвращает 200."""
        # Создаём двух пользователей через /users напрямую
        u1 = (await client.post("/users", json={"name": "liker_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "liker_2", "role": "seller", "skills": []})).json()

        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.status_code == 200

    async def test_like_response_has_required_fields(self, client: AsyncClient):
        """Ответ содержит все обязательные поля."""
        u1 = (await client.post("/users", json={"name": "lrf_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "lrf_2", "role": "seller", "skills": []})).json()

        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        data = resp.json()
        assert "like_id" in data
        assert "from_user_id" in data
        assert "to_user_id" in data
        assert "is_like" in data
        assert "is_match" in data

    async def test_like_is_true_stored(self, client: AsyncClient):
        """is_like=true сохраняется корректно."""
        u1 = (await client.post("/users", json={"name": "lit_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "lit_2", "role": "seller", "skills": []})).json()

        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.json()["is_like"] is True

    async def test_dislike_stored(self, client: AsyncClient):
        """is_like=false (дизлайк) сохраняется и is_match=false."""
        u1 = (await client.post("/users", json={"name": "dis_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "dis_2", "role": "seller", "skills": []})).json()

        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": False},
        )
        data = resp.json()
        assert data["is_like"] is False
        assert data["is_match"] is False

    async def test_like_self_returns_400(self, client: AsyncClient):
        """Лайк самого себя — 400."""
        u1 = (await client.post("/users", json={"name": "self_like", "role": "builder", "skills": []})).json()

        resp = await client.post(
            f"/api/v1/like/{u1['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.status_code == 400

    async def test_like_nonexistent_to_user_returns_404(self, client: AsyncClient):
        """Лайк несуществующего пользователя — 404."""
        u1 = (await client.post("/users", json={"name": "ghost_liker", "role": "builder", "skills": []})).json()

        resp = await client.post(
            "/api/v1/like/999999",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.status_code == 404

    async def test_like_nonexistent_from_user_returns_404(self, client: AsyncClient):
        """from_user_id несуществующий — 404."""
        u2 = (await client.post("/users", json={"name": "ghost_target", "role": "seller", "skills": []})).json()

        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": 999999, "is_like": True},
        )
        assert resp.status_code == 404

    async def test_update_like_to_dislike(self, client: AsyncClient):
        """Повторный POST меняет лайк на дизлайк."""
        u1 = (await client.post("/users", json={"name": "upd_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "upd_2", "role": "seller", "skills": []})).json()

        # Сначала лайк
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        # Потом дизлайк
        resp = await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": False})
        assert resp.json()["is_like"] is False


class TestMutualMatch:
    """Взаимный лайк → создание Match."""

    async def test_mutual_like_creates_match(self, client: AsyncClient):
        """A лайкает B, B лайкает A → is_match=True."""
        u1 = (await client.post("/users", json={"name": "mut_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "mut_2", "role": "seller", "skills": []})).json()

        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        resp = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})

        data = resp.json()
        assert data["is_match"] is True
        assert data["match_id"] is not None

    async def test_one_sided_like_no_match(self, client: AsyncClient):
        """Односторонний лайк → is_match=False."""
        u1 = (await client.post("/users", json={"name": "one_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "one_2", "role": "seller", "skills": []})).json()

        resp = await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        assert resp.json()["is_match"] is False

    async def test_mutual_match_has_score_when_profiles_exist(self, client: AsyncClient):
        """При взаимном лайке + founder_profiles у обоих — match_score заполнен."""
        # Онбордим обоих
        ob1 = await client.post("/onboarding", json=BUILDER_PROFILE)
        ob2 = await client.post("/onboarding", json=SELLER_PROFILE)
        assert ob1.status_code == 200
        assert ob2.status_code == 200

        # Получаем user_id через /users
        users_resp = await client.get("/users")
        users = users_resp.json() if isinstance(users_resp.json(), list) else []
        uid_map = {u["name"]: u["id"] for u in users}

        builder_uid = uid_map.get("like_test_builder")
        seller_uid = uid_map.get("like_test_seller")
        assert builder_uid and seller_uid, "Users not found after onboarding"

        # Взаимный лайк
        await client.post(f"/api/v1/like/{seller_uid}", json={"from_user_id": builder_uid, "is_like": True})
        resp = await client.post(f"/api/v1/like/{builder_uid}", json={"from_user_id": seller_uid, "is_like": True})

        data = resp.json()
        assert data["is_match"] is True
        assert data["match_score"] is not None
        assert 0 <= data["match_score"] <= 100

    async def test_dislike_prevents_match(self, client: AsyncClient):
        """A дизлайкает B, B лайкает A → is_match=False."""
        u1 = (await client.post("/users", json={"name": "dis_m1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "dis_m2", "role": "seller", "skills": []})).json()

        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": False})
        resp = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})

        assert resp.json()["is_match"] is False

    async def test_match_idempotent(self, client: AsyncClient):
        """Повторный взаимный лайк не создаёт дубль матча."""
        u1 = (await client.post("/users", json={"name": "idem_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "idem_2", "role": "seller", "skills": []})).json()

        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        r1 = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        # Повторный лайк
        r2 = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})

        assert r1.json()["match_id"] == r2.json()["match_id"]


class TestGetMatches:
    """GET /api/v1/matches?user_id={id}"""

    async def test_empty_matches_returns_200(self, client: AsyncClient):
        """Пользователь без матчей — 200, пустой список."""
        u1 = (await client.post("/users", json={"name": "nomatch", "role": "builder", "skills": []})).json()
        resp = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["matches"] == []

    async def test_matches_appear_after_mutual_like(self, client: AsyncClient):
        """После взаимного лайка матч появляется в GET /matches."""
        u1 = (await client.post("/users", json={"name": "gm_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "gm_2", "role": "seller", "skills": []})).json()

        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})

        resp = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        data = resp.json()
        assert data["total"] == 1
        assert data["matches"][0]["partner_user_id"] == u2["id"]

    async def test_matches_response_has_required_fields(self, client: AsyncClient):
        """MatchCard содержит все обязательные поля."""
        u1 = (await client.post("/users", json={"name": "mrf_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "mrf_2", "role": "seller", "skills": []})).json()

        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})

        resp = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        card = resp.json()["matches"][0]
        assert "match_id" in card
        assert "partner_user_id" in card
        assert "partner_name" in card
        assert "status" in card

    async def test_matches_nonexistent_user_returns_404(self, client: AsyncClient):
        """GET /matches для несуществующего user_id — 404."""
        resp = await client.get("/api/v1/matches?user_id=999999")
        assert resp.status_code == 404

    async def test_matches_visible_from_both_sides(self, client: AsyncClient):
        """Матч виден и у user_a и у user_b."""
        u1 = (await client.post("/users", json={"name": "both_1", "role": "builder", "skills": []})).json()
        u2 = (await client.post("/users", json={"name": "both_2", "role": "seller", "skills": []})).json()

        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})

        r1 = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        r2 = await client.get(f"/api/v1/matches?user_id={u2['id']}")

        assert r1.json()["total"] == 1
        assert r2.json()["total"] == 1
        assert r1.json()["matches"][0]["match_id"] == r2.json()["matches"][0]["match_id"]
