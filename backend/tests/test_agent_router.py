"""
test_agent_router.py — тесты для AgentRouter (D3).

Покрывают:
  - detect_mode() для каждого из трёх режимов
  - default-режим (advisor) для нейтральных сообщений
  - наличие непустого system_prompt у каждого режима
  - интеграцию в POST /api/v1/kristina/chat (поле `mode` в ответе)
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

from avatar_platform.agent_router import (
    AgentMode,
    MODE_SYSTEM_PROMPTS,
    detect_mode,
)
from agents.kristina_routes import kristina


PASSWORD = "TestPass123!"


async def _auth_headers(client: AsyncClient, email: str):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "name": "R"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['token']}"}


@pytest_asyncio.fixture(autouse=True)
async def _reset_kristina_memory():
    kristina.memories.clear()
    yield
    kristina.memories.clear()


# ─── UNIT: detect_mode ───────────────────────────────────────────────────────

def test_detect_mode_executor():
    decision = detect_mode("напиши user story для фичи логина")
    assert decision.mode == AgentMode.EXECUTOR
    assert decision.mode.value == "executor"
    assert decision.confidence > 0


def test_detect_mode_mentor():
    decision = detect_mode("у нас конфликт с партнёром, не знаю что делать")
    assert decision.mode == AgentMode.MENTOR
    assert decision.mode.value == "mentor"
    assert decision.confidence > 0


def test_detect_mode_advisor():
    decision = detect_mode("какая стратегия для выхода на рынок?")
    assert decision.mode == AgentMode.ADVISOR
    assert decision.mode.value == "advisor"
    assert decision.confidence > 0


def test_detect_mode_default():
    decision = detect_mode("привет")
    assert decision.mode == AgentMode.ADVISOR
    assert decision.confidence < 0.5


def test_system_prompt_not_empty():
    for mode in AgentMode:
        assert mode in MODE_SYSTEM_PROMPTS
        prompt = MODE_SYSTEM_PROMPTS[mode]
        assert isinstance(prompt, str)
        assert prompt.strip()
        decision = detect_mode("тестовый запрос режима")
        # Каждый режим имеет непустой system_prompt
        assert MODE_SYSTEM_PROMPTS[mode].strip()
        # RoutingDecision.system_prompt тоже непустой
        if decision.mode == mode:
            assert decision.system_prompt.strip()


# ─── INTEGRATION: mode в ответе /kristina/chat ───────────────────────────────

class TestChatResponseMode:

    async def test_chat_response_has_mode(self, client: AsyncClient):
        headers = await _auth_headers(client, "router1@test.syndi")
        resp = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "напиши user story для логина"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "mode" in data
        assert data["mode"] in ("advisor", "mentor", "executor")
        # "напиши" → executor
        assert data["mode"] == "executor"

    async def test_chat_response_mentor_mode(self, client: AsyncClient):
        headers = await _auth_headers(client, "router2@test.syndi")
        resp = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "у нас конфликт в команде, очень сложно"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["mode"] == "mentor"