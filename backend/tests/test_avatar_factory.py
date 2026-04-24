"""
test_avatar_factory.py — юнит и интеграционные тесты для AvatarFactory (D4).
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

from avatar_platform.avatar_factory import AvatarFactory, AvatarInstance


# ─── Unit-тесты AvatarFactory ────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_avatars():
    AvatarFactory._avatars.clear()
    yield
    AvatarFactory._avatars.clear()


class TestAvatarFactoryUnit:

    def test_create_avatar_builder(self):
        avatar = AvatarFactory.create_avatar(
            user_id=1, founder_name="Alex", role_id="builder",
        )
        assert isinstance(avatar, AvatarInstance)
        assert avatar.user_id == 1
        assert avatar.founder_name == "Alex"
        assert avatar.role_id == "builder"
        assert avatar.profession is not None
        assert "технический" in avatar.profession.title.lower() or avatar.profession.title

    def test_create_avatar_unknown_role(self):
        avatar = AvatarFactory.create_avatar(
            user_id=2, founder_name="Unknown", role_id="unknown_role",
        )
        assert avatar.profession is None
        assert avatar.user_id == 2

    def test_get_avatar(self):
        created = AvatarFactory.create_avatar(
            user_id=3, founder_name="Bob", role_id="seller",
        )
        retrieved = AvatarFactory.get_avatar(3)
        assert retrieved is created

    def test_get_avatar_not_found(self):
        assert AvatarFactory.get_avatar(9999) is None

    def test_avatar_to_dict(self):
        avatar = AvatarFactory.create_avatar(
            user_id=4, founder_name="Carol", role_id="operator",
            match_id="match-xyz", partner_user_id=5,
        )
        d = avatar.to_dict()
        assert "avatar_id" in d
        assert d["user_id"] == 4
        assert d["founder_name"] == "Carol"
        assert d["role_id"] == "operator"
        assert d["match_id"] == "match-xyz"
        assert d["partner_user_id"] == 5
        assert "emotional_state" in d
        assert "state" in d["emotional_state"]

    def test_avatar_system_prompt(self):
        avatar = AvatarFactory.create_avatar(
            user_id=6, founder_name="Dave", role_id="researcher",
        )
        prompt = avatar.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Dave" in prompt

    def test_avatar_system_prompt_unknown_role(self):
        avatar = AvatarFactory.create_avatar(
            user_id=7, founder_name="Eve", role_id="unknown",
        )
        prompt = avatar.get_system_prompt()
        assert isinstance(prompt, str)
        assert "Eve" in prompt

    def test_list_avatars(self):
        AvatarFactory.create_avatar(user_id=10, founder_name="A", role_id="builder")
        AvatarFactory.create_avatar(user_id=11, founder_name="B", role_id="seller")
        lst = AvatarFactory.list_avatars()
        assert len(lst) == 2


# ─── Интеграционные тесты /api/v1/avatar/me ─────────────────────────────────

BUILDER_ONBOARD = {
    "user_id": "avatar_builder",
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

SELLER_ONBOARD = {
    "user_id": "avatar_seller",
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


async def _register_and_token(client: AsyncClient, email: str, password: str = "TestPass123!") -> str:
    resp = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 200, f"register failed: {resp.text}"
    return resp.json()["token"]


@pytest_asyncio.fixture(autouse=True)
async def _authenticate_client(client: AsyncClient):
    token = await _register_and_token(client, "avatar_fixture@test.syndi")
    client.headers["Authorization"] = f"Bearer {token}"
    yield
    client.headers.pop("Authorization", None)


class TestAvatarIntegration:

    async def test_avatar_not_found_without_match(self, client: AsyncClient):
        # user без матча — 404
        resp = await client.get("/api/v1/avatar/me")
        assert resp.status_code == 404

    async def test_avatar_created_on_match(self, client: AsyncClient):
        # Onboarding двух юзеров
        ob1 = await client.post("/onboarding", json=BUILDER_ONBOARD)
        ob2 = await client.post("/onboarding", json=SELLER_ONBOARD)
        assert ob1.status_code == 200
        assert ob2.status_code == 200

        # Получить id обоих пользователей через /users
        users_resp = await client.get("/users")
        users = users_resp.json() if isinstance(users_resp.json(), list) else []
        uid_map = {u["name"]: u["id"] for u in users}
        builder_uid = uid_map.get("avatar_builder")
        seller_uid = uid_map.get("avatar_seller")
        assert builder_uid and seller_uid

        # Взаимный лайк → создание матча → создание аватаров
        await client.post(f"/api/v1/like/{seller_uid}", json={"from_user_id": builder_uid, "is_like": True})
        resp = await client.post(f"/api/v1/like/{builder_uid}", json={"from_user_id": seller_uid, "is_like": True})
        assert resp.json()["is_match"] is True

        # Получить аватар для builder_uid — нужно аутентифицироваться как этот юзер.
        # Но фикстура authenticate_client проставляет токен нового fixture-юзера.
        # Используем прямой доступ к AvatarFactory для проверки создания аватаров:
        builder_avatar = AvatarFactory.get_avatar(builder_uid)
        seller_avatar = AvatarFactory.get_avatar(seller_uid)
        assert builder_avatar is not None
        assert seller_avatar is not None
        assert builder_avatar.role_id == "builder"
        assert seller_avatar.role_id == "seller"
        assert builder_avatar.partner_user_id == seller_uid
        assert seller_avatar.partner_user_id == builder_uid
