"""
test_memory.py — тесты для D5: трёхуровневая память аватара.

Покрывает:
  - DialogMemory: add/get, max_limit, llm_context
  - SemanticMemory: add_fact, дедупликация, context_summary
  - PersistentMemory: save/get асинхронно через SQLite
  - MemoryManager: build_llm_context
  - /chat → /history: integration через PersistentMemory
"""
import pytest_asyncio
from httpx import AsyncClient

from avatar_platform.memory.dialog_memory import DialogMemory
from avatar_platform.memory.semantic_memory import SemanticMemory
from avatar_platform.memory.persistent_memory import PersistentMemory
from avatar_platform.memory.memory_manager import MemoryManager
from database.database import AsyncSessionLocal
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
    """Сбрасываем in-memory память Кристины (включая MemoryManager) перед каждым тестом."""
    kristina.memories.clear()
    kristina.memory_manager.dialog._sessions.clear()
    kristina.memory_manager.semantic._facts.clear()
    yield
    kristina.memories.clear()
    kristina.memory_manager.dialog._sessions.clear()
    kristina.memory_manager.semantic._facts.clear()


# ─── DialogMemory ────────────────────────────────────────────────────────────

class TestDialogMemory:

    def test_dialog_memory_add_get(self):
        mem = DialogMemory(max_messages=20)
        sid = "session-1"
        mem.add_message(sid, "user", "Привет")
        mem.add_message(sid, "assistant", "Здравствуй!")
        mem.add_message(sid, "user", "Как дела?")
        msgs = mem.get_messages(sid)
        assert len(msgs) == 3
        assert msgs[0]["role"] == "user"
        assert msgs[0]["content"] == "Привет"
        assert msgs[-1]["content"] == "Как дела?"

    def test_dialog_memory_max_limit(self):
        mem = DialogMemory(max_messages=20)
        sid = "s"
        for i in range(25):
            mem.add_message(sid, "user", f"msg {i}")
        msgs = mem.get_messages(sid, last_n=100)
        assert len(msgs) == 20
        # Должны остаться последние 20: 5..24
        assert msgs[0]["content"] == "msg 5"
        assert msgs[-1]["content"] == "msg 24"

    def test_dialog_memory_llm_context(self):
        mem = DialogMemory()
        sid = "s"
        mem.add_message(sid, "user", "A", agent_mode="advisor", mood="happy")
        mem.add_message(sid, "assistant", "B", agent_mode="advisor")
        ctx = mem.get_context_for_llm(sid)
        assert len(ctx) == 2
        for item in ctx:
            assert set(item.keys()) == {"role", "content"}

    def test_dialog_memory_clear(self):
        mem = DialogMemory()
        mem.add_message("s", "user", "x")
        assert mem.session_count() == 1
        mem.clear("s")
        assert mem.session_count() == 0


# ─── SemanticMemory ──────────────────────────────────────────────────────────

class TestSemanticMemory:

    def test_semantic_memory_add_fact(self):
        sm = SemanticMemory()
        sm.add_fact(42, "работает в UX", category="role")
        facts = sm.get_facts(42)
        assert "работает в UX" in facts

    def test_semantic_memory_deduplication(self):
        sm = SemanticMemory()
        sm.add_fact(1, "живёт в Москве")
        sm.add_fact(1, "живёт в Москве")
        sm.add_fact(1, "живёт в Москве")
        facts = sm.get_facts(1)
        assert facts.count("живёт в Москве") == 1

    def test_semantic_memory_context_summary(self):
        sm = SemanticMemory()
        assert sm.get_context_summary(1) == ""
        sm.add_fact(1, "UX-дизайнер")
        sm.add_fact(1, "любит кофе")
        summary = sm.get_context_summary(1)
        assert summary
        assert "UX-дизайнер" in summary
        assert "любит кофе" in summary

    def test_semantic_memory_category_filter(self):
        sm = SemanticMemory()
        sm.add_fact(1, "fact-a", category="cat_a")
        sm.add_fact(1, "fact-b", category="cat_b")
        cat_a = sm.get_facts(1, category="cat_a")
        assert "fact-a" in cat_a
        assert "fact-b" not in cat_a


# ─── PersistentMemory ────────────────────────────────────────────────────────

class TestPersistentMemory:

    async def test_persistent_memory_save_get(self):
        pm = PersistentMemory()
        async with AsyncSessionLocal() as db:
            ok = await pm.save_message(
                db, user_id=777, session_id="sess-x",
                role="user", content="hello persistent",
                memory_type="dialog", agent_mode="advisor",
            )
            assert ok is True

            await pm.save_message(
                db, user_id=777, session_id="sess-x",
                role="assistant", content="hi back",
                memory_type="dialog", mood="warm",
            )

            rows = await pm.get_history(db, user_id=777, session_id="sess-x")
            assert len(rows) == 2
            contents = {r["content"] for r in rows}
            assert "hello persistent" in contents
            assert "hi back" in contents
            roles = {r["role"] for r in rows}
            assert roles == {"user", "assistant"}
            user_row = next(r for r in rows if r["role"] == "user")
            assert user_row["agent_mode"] == "advisor"
            asst_row = next(r for r in rows if r["role"] == "assistant")
            assert asst_row["mood"] == "warm"

    async def test_persistent_memory_filter_by_session(self):
        pm = PersistentMemory()
        async with AsyncSessionLocal() as db:
            await pm.save_message(db, 1, "a", "user", "msg-a")
            await pm.save_message(db, 1, "b", "user", "msg-b")
            rows_a = await pm.get_history(db, user_id=1, session_id="a")
            rows_b = await pm.get_history(db, user_id=1, session_id="b")
            assert len(rows_a) == 1
            assert rows_a[0]["content"] == "msg-a"
            assert len(rows_b) == 1
            assert rows_b[0]["content"] == "msg-b"


# ─── MemoryManager ───────────────────────────────────────────────────────────

class TestMemoryManager:

    def test_memory_manager_build_context(self):
        mm = MemoryManager()
        sid = "sess-mm"
        mm.dialog.add_message(sid, "user", "hi")
        mm.dialog.add_message(sid, "assistant", "hello")
        mm.semantic.add_fact(1, "любит Python")

        messages, facts = mm.build_llm_context(user_id=1, session_id=sid)
        assert isinstance(messages, list)
        assert isinstance(facts, str)
        assert len(messages) == 2
        assert facts
        assert "Python" in facts

    def test_memory_manager_build_context_empty_facts(self):
        mm = MemoryManager()
        sid = "empty"
        mm.dialog.add_message(sid, "user", "hi")
        messages, facts = mm.build_llm_context(user_id=999, session_id=sid)
        assert messages
        assert facts == ""


# ─── /chat → /history (integration) ──────────────────────────────────────────

class TestChatStoresInMemory:

    async def test_chat_stores_in_memory(self, client: AsyncClient):
        headers, _ = await _auth_headers(client, "mem1@test.syndi", name="Mem1")
        session_id = "mem-sess-1"

        r1 = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Привет, я новый основатель", "session_id": session_id},
        )
        assert r1.status_code == 200, r1.text

        r2 = await client.post(
            "/api/v1/kristina/chat",
            headers=headers,
            json={"message": "Расскажи про UX исследование", "session_id": session_id},
        )
        assert r2.status_code == 200, r2.text

        hist = await client.get(
            f"/api/v1/kristina/history?session_id={session_id}",
            headers=headers,
        )
        assert hist.status_code == 200, hist.text
        data = hist.json()
        assert data["total"] >= 4, data
        # history должна содержать как минимум user-сообщение и ответ
        contents = [m.get("content", "") for m in data["messages"]]
        assert any("Привет" in c for c in contents)
