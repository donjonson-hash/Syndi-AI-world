"""
test_emotional_core.py — тесты для EmotionalCore (D2).
"""
import pytest
from httpx import AsyncClient

from avatar_platform.emotional_core import EmotionalCore
from agents.kristina_routes import kristina


PASSWORD = "TestPass123!"


@pytest.fixture(autouse=True)
def _reset_kristina_memory():
    kristina.memories.clear()
    yield
    kristina.memories.clear()


# ─── Unit tests (sync) ────────────────────────────────────────────────────────

class TestEmotionalCoreUnit:

    def test_emotional_core_init(self):
        core = EmotionalCore()
        assert core.state
        assert "energy" in core.state
        assert "happiness" in core.state
        assert "curiosity" in core.state
        assert all(0.0 <= v <= 1.0 for v in core.state.values())

    def test_evolve_returns_state(self):
        core = EmotionalCore()
        result = core.evolve()
        assert "state" in result
        assert "dominant_emotion" in result
        assert "mood_description" in result
        assert "llm_style_hint" in result
        assert isinstance(result["state"], dict)

    def test_evolve_with_positive_context(self):
        core = EmotionalCore()
        # Множество шагов нужно, т.к. _fluctuate даёт шум ±0.04
        # Зафиксируем стартовое значение и проверим направление тренда
        happiness_before = core.state["happiness"]
        for _ in range(20):
            core.evolve(context={"positive_tone": True})
        # При 20 шагах positive_tone→+0.15 happiness должна вырасти или быть близко к 1.0
        assert core.state["happiness"] >= happiness_before or core.state["happiness"] >= 0.9

    def test_evolve_with_negative_context(self):
        core = EmotionalCore()
        irritation_before = core.state["irritation"]
        for _ in range(20):
            core.evolve(context={"negative_tone": True})
        assert core.state["irritation"] > irritation_before or core.state["irritation"] >= 0.9

    def test_normalize_bounds(self):
        core = EmotionalCore()
        for _ in range(100):
            core.evolve(context={"positive_tone": True, "negative_tone": True})
        for k, v in core.state.items():
            assert 0.1 <= v <= 1.0, f"{k}={v} out of bounds"

    def test_big5_initialization(self):
        core = EmotionalCore(big5={"extraversion": 90, "neuroticism": 20})
        assert abs(core.traits["extraversion"] - 0.9) < 1e-6
        assert abs(core.traits["neuroticism"] - 0.2) < 1e-6


# ─── Integration test (async) ────────────────────────────────────────────────

class TestChatMood:

    async def test_chat_response_has_mood(self, client: AsyncClient):
        register = await client.post(
            "/api/v1/auth/register",
            json={"email": "mood1@test.syndi", "password": PASSWORD, "name": "MoodUser"},
        )
        assert register.status_code == 200, register.text
        token = register.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Привет"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "mood" in data
        # mood может быть null или строкой
        assert data["mood"] is None or isinstance(data["mood"], str)