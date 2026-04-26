import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Syndi AI API" in resp.json()["message"]

@pytest.mark.asyncio
async def test_auth_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com", "password": "testpass123", "name": "Test",
    })
    assert resp.status_code == 200
    assert resp.json()["access_token"]

@pytest.mark.asyncio
async def test_me_unauthorized(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
