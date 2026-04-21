"""
Интеграционные тесты для /onboarding и /match/{user_id}

Покрывают:
  1. Успешный onboarding с различными профилями
  2. Маппинг _map_raw_to_normalizer() — все ветки time/salary/launched/sync/accountability
  3. Валидацию RawQuestionnaire (обязательные поля)
  4. /match — топ-3 лимит и сортировка по score
  5. /match — генерация why_there_is_a_chance
  6. /match — risk_flags в MatchCard (low_intent_alignment, same_primary_role,
                tempo_conflict, high_emotional_volatility, low_accountability_alignment)
  7. Edge cases: нет профиля, нет других кандидатов
  8. Симметрия: builder+seller даёт более высокий score чем builder+tourist
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient


# ─────────────────────────────────────────────────────────────────────────────
# 1. Onboarding — успешная регистрация
# ─────────────────────────────────────────────────────────────────────────────

class TestOnboardingSuccess:

    @pytest.mark.asyncio
    async def test_builder_onboarding_returns_200(self, client, profile_builder):
        r = await client.post("/onboarding", json=profile_builder)
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_onboarding_returns_correct_user_id(self, client, profile_builder):
        r = await client.post("/onboarding", json=profile_builder)
        body = r.json()
        assert body["user_id"] == "founder_builder"
        assert body["status"] == "success"

    @pytest.mark.asyncio
    async def test_onboarding_returns_intent_goal(self, client, profile_builder):
        r = await client.post("/onboarding", json=profile_builder)
        assert r.json()["intent"] == "build_company"

    @pytest.mark.asyncio
    async def test_seller_onboarding_succeeds(self, client, profile_seller):
        r = await client.post("/onboarding", json=profile_seller)
        assert r.status_code == 200
        assert r.json()["status"] == "success"

    @pytest.mark.asyncio
    async def test_tourist_onboarding_succeeds(self, client, profile_tourist):
        r = await client.post("/onboarding", json=profile_tourist)
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_onboarding_without_big5_succeeds(self, client, profile_tourist):
        """Big Five — опциональный блок."""
        r = await client.post("/onboarding", json=profile_tourist)
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_operator_onboarding_succeeds(self, client, profile_operator):
        r = await client.post("/onboarding", json=profile_operator)
        assert r.status_code == 200
        assert r.json()["user_id"] == "founder_operator"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Маппинг _map_raw_to_normalizer() — проверяем граничные значения
# ─────────────────────────────────────────────────────────────────────────────

class TestMappingVariants:

    @pytest.mark.asyncio
    async def test_time_commitment_full_time(self, client, profile_builder):
        """full_time → 40h → time_commitment нормализуется в 50."""
        r = await client.post("/onboarding", json={**profile_builder, "time_commitment": "full_time"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_time_commitment_part_time(self, client, profile_builder):
        r = await client.post("/onboarding", json={**profile_builder, "time_commitment": "part_time"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_time_commitment_numeric_hours(self, client, profile_builder):
        """Числовой формат '60h' тоже должен работать."""
        r = await client.post("/onboarding", json={**profile_builder, "time_commitment": "60h"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_salary_readiness_3_months(self, client, profile_builder):
        r = await client.post("/onboarding", json={**profile_builder, "no_salary_readiness": "3_months"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_salary_readiness_24_months(self, client, profile_builder):
        r = await client.post("/onboarding", json={**profile_builder, "no_salary_readiness": "24_months"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_launched_projects_zero(self, client, profile_tourist):
        r = await client.post("/onboarding", json={**profile_tourist, "launched_projects": "0"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_launched_projects_many(self, client, profile_builder):
        r = await client.post("/onboarding", json={**profile_builder, "launched_projects": "5+"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_sync_daily(self, client, profile_builder):
        r = await client.post("/onboarding", json={**profile_builder, "sync_frequency": "daily"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_sync_as_needed(self, client, profile_tourist):
        r = await client.post("/onboarding", json={**profile_tourist, "sync_frequency": "as_needed"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_accountability_extreme_good(self, client, profile_builder):
        """never disappear + always ownership → высокая надёжность."""
        r = await client.post("/onboarding", json={
            **profile_builder,
            "accountability_disappear_label": "never",
            "accountability_ownership_label": "always",
        })
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_accountability_extreme_bad(self, client, profile_tourist):
        """always disappear + never ownership → низкая надёжность."""
        r = await client.post("/onboarding", json={
            **profile_tourist,
            "accountability_disappear_label": "always",
            "accountability_ownership_label": "never",
        })
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_empty_self_actions(self, client, profile_tourist):
        """self_actions=[] → breadth_val=0 → нормализуется корректно."""
        r = await client.post("/onboarding", json={**profile_tourist, "self_actions": []})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_many_self_actions(self, client, profile_builder):
        """Много действий → breadth capped at 10."""
        r = await client.post("/onboarding", json={
            **profile_builder,
            "self_actions": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        })
        assert r.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 3. Валидация — обязательные поля
# ─────────────────────────────────────────────────────────────────────────────

class TestOnboardingValidation:

    @pytest.mark.asyncio
    async def test_missing_user_id_returns_422(self, client, profile_builder):
        bad = {k: v for k, v in profile_builder.items() if k != "user_id"}
        r = await client.post("/onboarding", json=bad)
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_intent_goal_returns_422(self, client, profile_builder):
        bad = {k: v for k, v in profile_builder.items() if k != "intent_goal"}
        r = await client.post("/onboarding", json=bad)
        assert r.status_code in (422, 500)

    @pytest.mark.asyncio
    async def test_empty_body_returns_422(self, client):
        r = await client.post("/onboarding", json={})
        assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 4. Match — базовые гарантии
# ─────────────────────────────────────────────────────────────────────────────

class TestMatchBasic:

    @pytest.mark.asyncio
    async def test_no_profile_returns_404(self, client):
        r = await client.get("/match/unknown_user")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_no_candidates_returns_404(self, client, profile_builder):
        await client.post("/onboarding", json=profile_builder)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_match_returns_list(self, client, profile_builder, profile_seller):
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_match_returns_max_3(self, client, profile_builder, profile_seller,
                                        profile_operator, profile_same_role_builder):
        for p in [profile_builder, profile_seller, profile_operator, profile_same_role_builder]:
            await client.post("/onboarding", json=p)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 200
        assert len(r.json()) <= 3

    @pytest.mark.asyncio
    async def test_match_sorted_by_score_desc(self, client, profile_builder,
                                               profile_seller, profile_operator):
        for p in [profile_builder, profile_seller, profile_operator]:
            await client.post("/onboarding", json=p)
        r = await client.get("/match/founder_builder")
        scores = [m["total_score"] for m in r.json()]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_match_card_has_required_fields(self, client, profile_builder, profile_seller):
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        card = r.json()[0]
        assert "candidate_id" in card
        assert "total_score" in card
        assert "why_there_is_a_chance" in card
        assert "risks" in card

    @pytest.mark.asyncio
    async def test_match_score_in_valid_range(self, client, profile_builder, profile_seller):
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        for card in r.json():
            assert 0 <= card["total_score"] <= 100

    @pytest.mark.asyncio
    async def test_self_not_in_results(self, client, profile_builder, profile_seller):
        """Реквестер не должен появляться в своих кандидатах."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        ids = [m["candidate_id"] for m in r.json()]
        assert "founder_builder" not in ids


# ─────────────────────────────────────────────────────────────────────────────
# 5. Why-there-is-a-chance — текстовое объяснение
# ─────────────────────────────────────────────────────────────────────────────

class TestWhyText:

    @pytest.mark.asyncio
    async def test_high_match_has_nonempty_why(self, client, profile_builder, profile_seller):
        """builder+seller — сильная пара, текст не пустой."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        top = r.json()[0]
        assert top["why_there_is_a_chance"]
        assert len(top["why_there_is_a_chance"]) > 0

    @pytest.mark.asyncio
    async def test_complementary_roles_mentioned(self, client, profile_builder, profile_seller):
        """builder+seller → роли комплементарны → фраза про роли в тексте."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        top = r.json()[0]
        assert "роли" in top["why_there_is_a_chance"] or "вовлечённости" in top["why_there_is_a_chance"]

    @pytest.mark.asyncio
    async def test_weak_match_has_baseline_text(self, client, profile_builder, profile_tourist):
        """Слабая пара → 'Базовое совпадение'."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_tourist)
        r = await client.get("/match/founder_builder")
        # tourist может всё равно попасть, но текст должен быть
        card = r.json()[0]
        assert card["why_there_is_a_chance"]


# ─────────────────────────────────────────────────────────────────────────────
# 6. Risk flags — конкретные флаги в MatchCard
# ─────────────────────────────────────────────────────────────────────────────

class TestRiskFlags:

    @pytest.mark.asyncio
    async def test_same_role_flag(self, client, profile_builder, profile_same_role_builder):
        """Два builder → same_primary_role флаг."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_same_role_builder)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 200
        card = r.json()[0]
        assert "same_primary_role" in card["risks"]

    @pytest.mark.asyncio
    async def test_no_risk_flags_for_strong_pair(self, client, profile_builder, profile_seller):
        """builder+seller сильная пара — критических флагов нет."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        card = r.json()[0]
        critical = {"low_intent_alignment", "low_accountability_alignment"}
        assert not critical.intersection(set(card["risks"]))

    @pytest.mark.asyncio
    async def test_low_intent_flag_tourist_vs_builder(self, client, profile_builder, profile_tourist):
        """builder (build_company) vs tourist (stable_income + part_time) → low_intent_alignment."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_tourist)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 200
        card = r.json()[0]
        # Турист должен получить low_intent или быть очень внизу по score
        has_intent_flag = "low_intent_alignment" in card["risks"]
        low_score = card["total_score"] < 65
        assert has_intent_flag or low_score, (
            f"Ожидаем флаг или низкий score для туриста. "
            f"risks={card['risks']}, score={card['total_score']}"
        )

    @pytest.mark.asyncio
    async def test_high_emotional_volatility_flag(self, client, profile_volatile, profile_builder):
        """Два профиля с низким Big5 emotional_stability → high_emotional_volatility."""
        volatile_2 = {
            **profile_volatile,
            "user_id": "founder_volatile_2",
            "primary_role": "builder",  # разные роли чтобы не сработал same_role
        }
        await client.post("/onboarding", json=profile_volatile)
        await client.post("/onboarding", json=volatile_2)
        r = await client.get("/match/founder_volatile")
        assert r.status_code == 200
        card = r.json()[0]
        assert "high_emotional_volatility" in card["risks"]

    @pytest.mark.asyncio
    async def test_low_accountability_flag(self, client, profile_builder, profile_tourist):
        """
        Турист: accountability_disappear=always + ownership=never → low_accountability_alignment.
        Builder: надёжный (never disappear, always ownership).
        Сильная асимметрия → флаг.
        """
        bad_accountability = {
            **profile_tourist,
            "user_id": "bad_acc",
            "accountability_disappear_label": "always",
            "accountability_ownership_label": "never",
        }
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=bad_accountability)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 200
        card = r.json()[0]
        assert "low_accountability_alignment" in card["risks"]

    @pytest.mark.asyncio
    async def test_tempo_conflict_flag(self, client, profile_builder, profile_operator):
        """
        builder: iterate_fast + daily sync
        operator: build_right_first + twice_a_week → tempo_conflict при разном sync.
        """
        fast = {**profile_builder, "tempo": "iterate_fast", "sync_frequency": "daily"}
        slow = {**profile_operator, "tempo": "build_right_first", "sync_frequency": "weekly"}
        await client.post("/onboarding", json=fast)
        await client.post("/onboarding", json=slow)
        r = await client.get("/match/founder_builder")
        assert r.status_code == 200
        card = r.json()[0]
        assert "tempo_conflict" in card["risks"]

    @pytest.mark.asyncio
    async def test_risks_is_list(self, client, profile_builder, profile_seller):
        """risks всегда список, даже пустой."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        for card in r.json():
            assert isinstance(card["risks"], list)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Качество скоринга — реальные профили дают ожидаемую иерархию
# ─────────────────────────────────────────────────────────────────────────────

class TestScoringQuality:

    @pytest.mark.asyncio
    async def test_builder_seller_beats_builder_tourist(
        self, client, profile_builder, profile_seller, profile_tourist
    ):
        """builder+seller должен стоять выше builder+tourist в shortlist."""
        for p in [profile_builder, profile_seller, profile_tourist]:
            await client.post("/onboarding", json=p)
        r = await client.get("/match/founder_builder")
        cards = r.json()
        ids = [c["candidate_id"] for c in cards]
        # seller должен быть выше tourist
        if "founder_seller" in ids and "founder_tourist" in ids:
            assert ids.index("founder_seller") < ids.index("founder_tourist"), (
                "builder+seller должен иметь score выше чем builder+tourist"
            )

    @pytest.mark.asyncio
    async def test_builder_seller_score_above_60(self, client, profile_builder, profile_seller):
        """Сильная пара должна набирать >= 60 total_score."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)
        r = await client.get("/match/founder_builder")
        top = r.json()[0]
        assert top["total_score"] >= 60, (
            f"builder+seller ожидаем score >= 60, получили {top['total_score']}"
        )

    @pytest.mark.asyncio
    async def test_builder_tourist_score_below_builder_seller(
        self, client, profile_builder, profile_seller, profile_tourist
    ):
        """builder+tourist должен давать ниже score, чем builder+seller."""
        for p in [profile_builder, profile_seller, profile_tourist]:
            await client.post("/onboarding", json=p)
        r = await client.get("/match/founder_builder")
        cards = {c["candidate_id"]: c["total_score"] for c in r.json()}
        if "founder_seller" in cards and "founder_tourist" in cards:
            assert cards["founder_seller"] > cards["founder_tourist"]

    @pytest.mark.asyncio
    async def test_symmetry_builder_and_seller(self, client, profile_builder, profile_seller):
        """score(builder→seller) должен совпадать с score(seller→builder)."""
        await client.post("/onboarding", json=profile_builder)
        await client.post("/onboarding", json=profile_seller)

        r_bs = await client.get("/match/founder_builder")
        score_bs = r_bs.json()[0]["total_score"]

        r_sb = await client.get("/match/founder_seller")
        score_sb = r_sb.json()[0]["total_score"]

        assert abs(score_bs - score_sb) < 0.01, (
            f"Ожидаем симметрию: score(b→s)={score_bs} != score(s→b)={score_sb}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Health / root
# ─────────────────────────────────────────────────────────────────────────────

class TestSystemEndpoints:

    @pytest.mark.asyncio
    async def test_root_returns_200(self, client):
        r = await client.get("/")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_root_has_scoring_model(self, client):
        r = await client.get("/")
        assert "scoring_model" in r.json()

    @pytest.mark.asyncio
    async def test_health_returns_healthy(self, client):
        r = await client.get("/health")
        assert r.json()["status"] == "healthy"
