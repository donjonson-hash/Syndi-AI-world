import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from database.database import engine, Base


@pytest_asyncio.fixture(autouse=True)
async def setup_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Syndi AI" in resp.json()["name"]


@pytest.mark.asyncio
async def test_auth_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com", "password": "testpass123", "name": "Test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data or "access_token" in data


@pytest.mark.asyncio
async def test_me_unauthorized(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
