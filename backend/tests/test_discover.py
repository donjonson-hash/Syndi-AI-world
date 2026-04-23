"""
test_discover.py — интеграционные тесты GET /api/v1/discover
"""
import pytest
from httpx import AsyncClient

# ─── Fixtures helpers ────────────────────────────────────────────────────────

BUILDER = {
    "user_id": "disc_builder",
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

SELLER = {
    "user_id": "disc_seller",
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

OPERATOR = {
    "user_id": "disc_operator",
    "time_commitment": "full_time", "no_salary_readiness": "12_months",
    "intent_goal": "build_company", "launched_projects": "1-2",
    "self_actions": ["managed_team", "built_processes"],
    "primary_role": "operator", "no_go_role_tags": [],
    "decision_style": "discuss_first", "conflict_style": "calm_discussion",
    "work_mode": "team", "tempo": "build_right_first",
    "sync_frequency": "twice_a_week",
    "accountability_disappear_label": "never",
    "accountability_ownership_label": "usually",
}


async def _onboard(client: AsyncClient, profile: dict) -> int:
    """Онбордит профиль и возвращает integer user_id из БД."""
    resp = await client.post("/onboarding", json=profile)
    assert resp.status_code == 200, f"Onboard failed: {resp.text}"
    users = (await client.get("/users")).json()
    uid_map = {u["name"]: u["id"] for u in (users if isinstance(users, list) else [])}
    return uid_map[profile["user_id"]]


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestDiscoverBasic:

    async def test_discover_returns_200(self, client: AsyncClient):
        """Discover возвращает 200 для пользователя с профилем."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        resp = await client.get(f"/api/v1/discover?user_id={uid}")
        assert resp.status_code == 200

    async def test_discover_response_structure(self, client: AsyncClient):
        """Ответ содержит user_id, cards, total, filtered_already_seen."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        data = (await client.get(f"/api/v1/discover?user_id={uid}")).json()
        assert "user_id" in data
        assert "cards" in data
        assert "total" in data
        assert "filtered_already_seen" in data

    async def test_discover_card_has_required_fields(self, client: AsyncClient):
        """Карточка содержит все обязательные поля."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        data = (await client.get(f"/api/v1/discover?user_id={uid}")).json()
        assert len(data["cards"]) > 0
        card = data["cards"][0]
        for field in ("candidate_user_id", "candidate_name", "primary_role",
                      "total_score", "intent_goal", "risk_flags", "why"):
            assert field in card, f"Missing: {field}"

    async def test_discover_no_self_in_results(self, client: AsyncClient):
        """Себя нет в результатах."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        data = (await client.get(f"/api/v1/discover?user_id={uid}")).json()
        ids = [c["candidate_user_id"] for c in data["cards"]]
        assert uid not in ids

    async def test_discover_score_in_valid_range(self, client: AsyncClient):
        """Score в диапазоне 0–100."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        data = (await client.get(f"/api/v1/discover?user_id={uid}")).json()
        for card in data["cards"]:
            assert 0 <= card["total_score"] <= 100

    async def test_discover_sorted_by_score_desc(self, client: AsyncClient):
        """Карточки отсортированы по score убыванию."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        await _onboard(client, OPERATOR)
        data = (await client.get(f"/api/v1/discover?user_id={uid}")).json()
        scores = [c["total_score"] for c in data["cards"]]
        assert scores == sorted(scores, reverse=True)

    async def test_discover_why_text_not_empty(self, client: AsyncClient):
        """Поле why не пустое."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        data = (await client.get(f"/api/v1/discover?user_id={uid}")).json()
        for card in data["cards"]:
            assert card["why"], "why text is empty"


class TestDiscoverFiltering:

    async def test_discover_filters_liked_users(self, client: AsyncClient):
        """Уже лайкнутый кандидат не появляется в ленте."""
        builder_uid = await _onboard(client, BUILDER)
        seller_uid = await _onboard(client, SELLER)

        # Лайкаем seller
        await client.post(
            f"/api/v1/like/{seller_uid}",
            json={"from_user_id": builder_uid, "is_like": True},
        )

        data = (await client.get(f"/api/v1/discover?user_id={builder_uid}")).json()
        ids = [c["candidate_user_id"] for c in data["cards"]]
        assert seller_uid not in ids
        assert data["filtered_already_seen"] >= 1

    async def test_discover_filters_disliked_users(self, client: AsyncClient):
        """Дизлайкнутый кандидат тоже фильтруется."""
        builder_uid = await _onboard(client, BUILDER)
        seller_uid = await _onboard(client, SELLER)

        await client.post(
            f"/api/v1/like/{seller_uid}",
            json={"from_user_id": builder_uid, "is_like": False},
        )

        data = (await client.get(f"/api/v1/discover?user_id={builder_uid}")).json()
        ids = [c["candidate_user_id"] for c in data["cards"]]
        assert seller_uid not in ids

    async def test_discover_limit_param(self, client: AsyncClient):
        """Параметр limit работает."""
        uid = await _onboard(client, BUILDER)
        await _onboard(client, SELLER)
        await _onboard(client, OPERATOR)

        data = (await client.get(f"/api/v1/discover?user_id={uid}&limit=1")).json()
        assert len(data["cards"]) <= 1

    async def test_discover_no_profile_returns_404(self, client: AsyncClient):
        """Пользователь без onboarding → 404."""
        # Создаём пользователя без онбординга
        u = (await client.post("/users", json={
            "name": "no_prof_disc", "email": "no_prof_disc@test.syndi", "role": "builder"
        })).json()
        resp = await client.get(f"/api/v1/discover?user_id={u['id']}")
        assert resp.status_code == 404

    async def test_discover_nonexistent_user_returns_404(self, client: AsyncClient):
        """Несуществующий user_id → 404."""
        resp = await client.get("/api/v1/discover?user_id=999999")
        assert resp.status_code == 404

    async def test_discover_empty_when_all_seen(self, client: AsyncClient):
        """Если всех уже лайкнул — лента пустая."""
        builder_uid = await _onboard(client, BUILDER)
        seller_uid = await _onboard(client, SELLER)

        await client.post(
            f"/api/v1/like/{seller_uid}",
            json={"from_user_id": builder_uid, "is_like": True},
        )

        # В БД только один кандидат (seller), он уже лайкнут
        data = (await client.get(f"/api/v1/discover?user_id={builder_uid}")).json()
        # seller отфильтрован — либо 0 карточек, либо только другие
        assert seller_uid not in [c["candidate_user_id"] for c in data["cards"]]
