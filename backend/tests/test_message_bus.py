"""
test_message_bus.py — юнит и интеграционные тесты для MessageBus (E2).
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

from avatar_platform.message_bus import MessageBus, MessageType, BusMessage


# ─── Reset MessageBus state per-test ──────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_bus():
    MessageBus._instance = None
    MessageBus._channels = {}
    MessageBus._handlers = {}
    yield
    MessageBus._instance = None
    MessageBus._channels = {}
    MessageBus._handlers = {}


# ─── Unit-тесты MessageBus ────────────────────────────────────────────────────

class TestMessageBusUnit:

    def test_message_bus_singleton(self):
        a = MessageBus.get_instance()
        b = MessageBus.get_instance()
        assert a is b

    def test_send_message(self):
        bus = MessageBus.get_instance()
        msg = bus.send(1, 2, MessageType.INSIGHT, {"text": "hi"})
        assert isinstance(msg, BusMessage)
        assert msg.from_user_id == 1
        assert msg.to_user_id == 2
        assert msg.message_type == MessageType.INSIGHT
        assert msg.payload == {"text": "hi"}
        assert msg.read is False
        assert msg.msg_id
        assert msg.timestamp

    def test_get_messages_symmetric(self):
        bus = MessageBus.get_instance()
        bus.send(1, 2, MessageType.STATUS_UPDATE, {"status": "active"})
        # Запрос с обратным порядком user-ов должен вернуть то же сообщение
        msgs_ab = bus.get_messages(1, 2)
        msgs_ba = bus.get_messages(2, 1)
        assert len(msgs_ab) == 1
        assert len(msgs_ba) == 1
        assert msgs_ab[0].msg_id == msgs_ba[0].msg_id

    def test_unread_count(self):
        bus = MessageBus.get_instance()
        bus.send(1, 2, MessageType.TASK_ASSIGNED, {"task": "a"})
        bus.send(1, 2, MessageType.TASK_ASSIGNED, {"task": "b"})
        bus.send(1, 2, MessageType.TASK_ASSIGNED, {"task": "c"})
        assert bus.get_unread_count(2) == 3
        assert bus.get_unread_count(1) == 0

    def test_mark_read(self):
        bus = MessageBus.get_instance()
        bus.send(1, 2, MessageType.INSIGHT, {"x": 1})
        bus.send(1, 2, MessageType.INSIGHT, {"x": 2})
        marked = bus.mark_read(1, 2)
        assert marked == 2
        assert bus.get_unread_count(2) == 0

    def test_get_messages_unread_only(self):
        bus = MessageBus.get_instance()
        bus.send(1, 2, MessageType.INSIGHT, {"x": 1})
        bus.mark_read(1, 2)
        bus.send(1, 2, MessageType.INSIGHT, {"x": 2})
        unread = bus.get_messages(1, 2, unread_only=True)
        assert len(unread) == 1
        assert unread[0].payload == {"x": 2}

    def test_channel_summary(self):
        bus = MessageBus.get_instance()
        bus.send(1, 2, MessageType.CONTEXT_SYNC, {"a": 1})
        bus.send(2, 1, MessageType.STATUS_UPDATE, {"b": 2})
        summary = bus.channel_summary(1, 2)
        assert summary["total_messages"] == 2
        assert summary["unread"] == 2
        assert summary["last_message"] is not None
        assert set(summary["message_types"]) >= {MessageType.CONTEXT_SYNC, MessageType.STATUS_UPDATE}

    def test_channel_summary_empty(self):
        bus = MessageBus.get_instance()
        summary = bus.channel_summary(99, 100)
        assert summary["total_messages"] == 0
        assert summary["unread"] == 0
        assert summary["last_message"] is None
        assert summary["message_types"] == []

    def test_broadcast_context_sync(self):
        bus = MessageBus.get_instance()
        bus.broadcast_context_sync(
            match_id="match-xyz",
            user_a_id=1,
            user_b_id=2,
            context={"match_score": 87.5, "roles": {"1": "builder", "2": "seller"}},
        )
        msgs = bus.get_messages(1, 2)
        assert len(msgs) == 2
        assert all(m.message_type == MessageType.CONTEXT_SYNC for m in msgs)
        # Один a→b, один b→a
        senders = {m.from_user_id for m in msgs}
        assert senders == {1, 2}
        for m in msgs:
            assert m.payload["match_id"] == "match-xyz"
            assert m.payload["initiator"] == 1
            assert m.payload["context"]["match_score"] == 87.5


# ─── Интеграционные тесты API ────────────────────────────────────────────────

async def _register_and_token(client: AsyncClient, email: str, password: str = "TestPass123!") -> str:
    resp = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 200, f"register failed: {resp.text}"
    return resp.json()["token"]


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    token = await _register_and_token(client, "msgbus_user@test.syndi")
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    client.headers.pop("Authorization", None)


class TestMessageBusAPI:

    async def test_api_send_message(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/avatar/messages", json={
            "to_user_id": 999,
            "message_type": "insight",
            "payload": {"note": "ping"},
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["sent"] is True
        assert data["msg_id"]

    async def test_api_send_message_invalid_type(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/avatar/messages", json={
            "to_user_id": 999,
            "message_type": "not_a_real_type",
            "payload": {},
        })
        assert resp.status_code == 422

    async def test_api_get_messages(self, auth_client: AsyncClient):
        # Сначала отправим сообщение
        await auth_client.post("/api/v1/avatar/messages", json={
            "to_user_id": 999,
            "message_type": "status_update",
            "payload": {"s": "ok"},
        })
        resp = await auth_client.get("/api/v1/avatar/messages", params={"partner_user_id": 999})
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
        assert "total" in data
        assert "unread_count" in data
        assert data["total"] >= 1

    async def test_api_mark_read(self, auth_client: AsyncClient):
        await auth_client.post("/api/v1/avatar/messages", json={
            "to_user_id": 999,
            "message_type": "alert",
            "payload": {"level": "warn"},
        })
        resp = await auth_client.post("/api/v1/avatar/messages/read", json={
            "partner_user_id": 999,
        })
        assert resp.status_code == 200
        assert "marked_read" in resp.json()

    async def test_api_channel_summary(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/avatar/channel", params={"partner_user_id": 999})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_messages" in data
        assert "unread" in data
        assert "last_message" in data
        assert "message_types" in data

    async def test_api_requires_auth(self, client: AsyncClient):
        # Без токена должно отвалиться
        resp = await client.get("/api/v1/avatar/messages", params={"partner_user_id": 1})
        assert resp.status_code == 401
