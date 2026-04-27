"""
test_kristina.py — тесты для Kristina AI agent (C7).

Покрывает:
  - GET  /api/v1/kristina/status  (публичный)
  - POST /api/v1/kristina/chat    (JWT)
  - GET  /api/v1/kristina/history (JWT)
  - Continuity памяти по session_id
  - Graceful fallback если LLM кидает исключение
"""
import pytest_asyncio
from httpx import AsyncClient

from agents.kristina_routes import kristina


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


@pytest_asyncio.fixture(autouse=True)
async def _reset_kristina_memory():
    """Очищаем in-memory память Кристины перед каждым тестом."""
    kristina.memories.clear()
    yield
    kristina.memories.clear()


# ─── STATUS ──────────────────────────────────────────────────────────────────

class TestStatus:
    async def test_kristina_status(self, client: AsyncClient):
        resp = await client.get("/api/v1/kristina/status")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "status" in data
        assert "agent" in data
        assert data["status"] == "active"
        assert "llm_available" in data
        assert isinstance(data["llm_available"], bool)


# ─── CHAT ────────────────────────────────────────────────────────────────────

class TestChat:

    async def test_chat_unauthorized(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/kristina/chat",
            json={"message": "Привет"},
        )
        assert resp.status_code == 401

    async def test_chat_basic(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "k1@test.syndi", name="K1")
        resp = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Привет"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "response" in data
        assert "session_id" in data
        assert data["agent"] == "kristina"

    async def test_chat_returns_string_response(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "k2@test.syndi", name="K2")
        resp = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Расскажи про UX исследование"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    async def test_chat_session_continuity(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "k3@test.syndi", name="K3")
        session_id = "continuity-session-1"

        r1 = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Привет", "session_id": session_id},
        )
        assert r1.status_code == 200, r1.text
        assert r1.json()["session_id"] == session_id

        r2 = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Помоги с проектом", "session_id": session_id},
        )
        assert r2.status_code == 200, r2.text

        hist = await client.get(
            f"/api/v1/kristina/history?session_id={session_id}",
            headers=headers,
        )
        assert hist.status_code == 200, hist.text
        data = hist.json()
        # 2 user + 2 assistant = 4 сообщения
        assert data["total"] >= 4
        assert data["session_id"] == session_id


# ─── HISTORY ─────────────────────────────────────────────────────────────────

class TestHistory:

    async def test_chat_history_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/kristina/history")
        assert resp.status_code == 401

    async def test_chat_history(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "k4@test.syndi", name="K4")

        # Сначала отправим сообщение
        await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Привет"},
        )

        resp = await client.get("/api/v1/kristina/history", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert data["total"] == len(data["messages"])


# ─── FALLBACK ────────────────────────────────────────────────────────────────

class TestFallback:

    async def test_chat_fallback_on_llm_error(self, client: AsyncClient, monkeypatch):
        """Даже если process_message кидает исключение, endpoint возвращает 200."""
        async def boom(*args, **kwargs):
            raise RuntimeError("LLM is unavailable")

        monkeypatch.setattr(kristina, "process_message", boom)

        headers, _ = await _auth_headers(client, "k5@test.syndi", name="K5")
        resp = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Привет"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        # Fallback-текст должен быть дружелюбным (содержать "Кристина")
        assert "Кристина" in data["response"]
