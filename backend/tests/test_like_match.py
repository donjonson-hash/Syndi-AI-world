"""
test_like_match.py — интеграционные тесты для like/match механики.

POST /api/v1/like/{to_user_id}
GET  /api/v1/matches?user_id={id}
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient


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


async def _create_user(client: AsyncClient, tag: str, role: str = "builder") -> dict:
    """Создаёт пользователя с уникальным email и возвращает {"id", "name"}."""
    resp = await client.post("/users", json={
        "name": tag,
        "email": f"{tag}@test.syndi",
        "role": role,
    })
    assert resp.status_code == 200, f"create_user failed ({tag}): {resp.text}"
    return resp.json()


async def _get_token(client: AsyncClient, email: str, password: str = "TestPass123!") -> str:
    """Регистрирует пользователя через /api/v1/auth/register и возвращает JWT-токен."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password,
    })
    assert resp.status_code == 200, f"register failed: {resp.text}"
    return resp.json()["token"]


async def _auth_header(client: AsyncClient, tag: str = "auth") -> dict:
    """Возвращает headers с валидным Bearer-токеном для произвольного пользователя."""
    token = await _get_token(client, f"{tag}_auth@test.syndi")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(autouse=True)
async def _authenticate_client(client: AsyncClient):
    """Регистрирует служебного пользователя и проставляет Bearer-токен в client.headers.

    Все эндпоинты /api/v1/like и /api/v1/matches требуют JWT; этот autouse-фикстур
    избавляет от необходимости прописывать заголовок в каждом вызове.
    """
    token = await _get_token(client, "like_match_fixture@test.syndi")
    client.headers["Authorization"] = f"Bearer {token}"
    yield
    client.headers.pop("Authorization", None)


# ─────────────────────────────────────────────────────────────────────────────
# Test Classes
# ─────────────────────────────────────────────────────────────────────────────

class TestLikeEndpoint:
    """POST /api/v1/like/{to_user_id}"""

    async def test_like_returns_200(self, client: AsyncClient):
        u1 = await _create_user(client, "lr200_1")
        u2 = await _create_user(client, "lr200_2", "seller")
        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.status_code == 200

    async def test_like_response_has_required_fields(self, client: AsyncClient):
        u1 = await _create_user(client, "lrf1_1")
        u2 = await _create_user(client, "lrf1_2", "seller")
        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        data = resp.json()
        for field in ("like_id", "from_user_id", "to_user_id", "is_like", "is_match"):
            assert field in data, f"Missing field: {field}"

    async def test_like_is_true_stored(self, client: AsyncClient):
        u1 = await _create_user(client, "lit1_1")
        u2 = await _create_user(client, "lit1_2", "seller")
        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.json()["is_like"] is True

    async def test_dislike_stored(self, client: AsyncClient):
        u1 = await _create_user(client, "dis1_1")
        u2 = await _create_user(client, "dis1_2", "seller")
        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": u1["id"], "is_like": False},
        )
        data = resp.json()
        assert data["is_like"] is False
        assert data["is_match"] is False

    async def test_like_self_returns_400(self, client: AsyncClient):
        u1 = await _create_user(client, "self_like1")
        resp = await client.post(
            f"/api/v1/like/{u1['id']}",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.status_code == 400

    async def test_like_nonexistent_to_user_returns_404(self, client: AsyncClient):
        u1 = await _create_user(client, "ghost_lkr1")
        resp = await client.post(
            "/api/v1/like/999999",
            json={"from_user_id": u1["id"], "is_like": True},
        )
        assert resp.status_code == 404

    async def test_like_nonexistent_from_user_returns_404(self, client: AsyncClient):
        u2 = await _create_user(client, "ghost_tgt1", "seller")
        resp = await client.post(
            f"/api/v1/like/{u2['id']}",
            json={"from_user_id": 999999, "is_like": True},
        )
        assert resp.status_code == 404

    async def test_update_like_to_dislike(self, client: AsyncClient):
        u1 = await _create_user(client, "upd_l1")
        u2 = await _create_user(client, "upd_l2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        resp = await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": False})
        assert resp.json()["is_like"] is False


class TestMutualMatch:
    """Взаимный лайк → создание Match."""

    async def test_mutual_like_creates_match(self, client: AsyncClient):
        u1 = await _create_user(client, "mut_m1")
        u2 = await _create_user(client, "mut_m2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        resp = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        data = resp.json()
        assert data["is_match"] is True
        assert data["match_id"] is not None

    async def test_one_sided_like_no_match(self, client: AsyncClient):
        u1 = await _create_user(client, "one_m1")
        u2 = await _create_user(client, "one_m2", "seller")
        resp = await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        assert resp.json()["is_match"] is False

    async def test_mutual_match_has_score_when_profiles_exist(self, client: AsyncClient):
        """При взаимном лайке + founder_profiles — match_score заполнен."""
        ob1 = await client.post("/onboarding", json=BUILDER_PROFILE)
        ob2 = await client.post("/onboarding", json=SELLER_PROFILE)
        assert ob1.status_code == 200, f"Builder onboard: {ob1.text}"
        assert ob2.status_code == 200, f"Seller onboard: {ob2.text}"

        users_resp = await client.get("/users")
        users = users_resp.json() if isinstance(users_resp.json(), list) else []
        uid_map = {u["name"]: u["id"] for u in users}

        builder_uid = uid_map.get("like_test_builder")
        seller_uid = uid_map.get("like_test_seller")
        assert builder_uid and seller_uid, f"Users not found, got: {list(uid_map.keys())}"

        await client.post(f"/api/v1/like/{seller_uid}", json={"from_user_id": builder_uid, "is_like": True})
        resp = await client.post(f"/api/v1/like/{builder_uid}", json={"from_user_id": seller_uid, "is_like": True})

        data = resp.json()
        assert data["is_match"] is True
        assert data["match_score"] is not None
        assert 0 <= data["match_score"] <= 100

    async def test_dislike_prevents_match(self, client: AsyncClient):
        u1 = await _create_user(client, "dispm1")
        u2 = await _create_user(client, "dispm2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": False})
        resp = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        assert resp.json()["is_match"] is False

    async def test_match_idempotent(self, client: AsyncClient):
        u1 = await _create_user(client, "idem_m1")
        u2 = await _create_user(client, "idem_m2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        r1 = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        r2 = await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        assert r1.json()["match_id"] == r2.json()["match_id"]


class TestGetMatches:
    """GET /api/v1/matches?user_id={id}"""

    async def test_empty_matches_returns_200(self, client: AsyncClient):
        u1 = await _create_user(client, "nomatch_u1")
        resp = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["matches"] == []

    async def test_matches_appear_after_mutual_like(self, client: AsyncClient):
        u1 = await _create_user(client, "gm_u1")
        u2 = await _create_user(client, "gm_u2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        resp = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        data = resp.json()
        assert data["total"] == 1
        assert data["matches"][0]["partner_user_id"] == u2["id"]

    async def test_matches_response_has_required_fields(self, client: AsyncClient):
        u1 = await _create_user(client, "mrf_u1")
        u2 = await _create_user(client, "mrf_u2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        resp = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        card = resp.json()["matches"][0]
        for field in ("match_id", "partner_user_id", "partner_name", "status"):
            assert field in card, f"Missing field: {field}"

    async def test_matches_nonexistent_user_returns_404(self, client: AsyncClient):
        resp = await client.get("/api/v1/matches?user_id=999999")
        assert resp.status_code == 404

    async def test_matches_visible_from_both_sides(self, client: AsyncClient):
        u1 = await _create_user(client, "both_u1")
        u2 = await _create_user(client, "both_u2", "seller")
        await client.post(f"/api/v1/like/{u2['id']}", json={"from_user_id": u1["id"], "is_like": True})
        await client.post(f"/api/v1/like/{u1['id']}", json={"from_user_id": u2["id"], "is_like": True})
        r1 = await client.get(f"/api/v1/matches?user_id={u1['id']}")
        r2 = await client.get(f"/api/v1/matches?user_id={u2['id']}")
        assert r1.json()["total"] == 1
        assert r2.json()["total"] == 1
        assert r1.json()["matches"][0]["match_id"] == r2.json()["matches"][0]["match_id"]
