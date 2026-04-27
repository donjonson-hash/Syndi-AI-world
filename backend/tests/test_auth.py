"""
test_auth.py — интеграционные тесты /api/v1/auth/{register,login,me}.

Использует общий conftest.py (httpx.AsyncClient + SQLite in-memory).
"""
from httpx import AsyncClient
from jose import jwt

from auth import SECRET_KEY, ALGORITHM


EMAIL_A = "founder_a@test.syndi"
EMAIL_B = "founder_b@test.syndi"
PASSWORD = "StrongPass123!"


async def _register(client: AsyncClient, email: str, password: str = PASSWORD, name: str | None = None):
    body = {"email": email, "password": password}
    if name:
        body["name"] = name
    return await client.post("/api/v1/auth/register", json=body)


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await _register(client, EMAIL_A, name="Alpha")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["email"] == EMAIL_A
        assert isinstance(data["id"], int)
        assert isinstance(data["token"], str) and len(data["token"]) > 10

    async def test_register_duplicate_email(self, client: AsyncClient):
        r1 = await _register(client, EMAIL_A)
        assert r1.status_code == 200, r1.text
        r2 = await _register(client, EMAIL_A)
        assert r2.status_code == 400


class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        reg = await _register(client, EMAIL_A)
        assert reg.status_code == 200
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": EMAIL_A, "password": PASSWORD},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data["token"], str) and len(data["token"]) > 10
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        await _register(client, EMAIL_A)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": EMAIL_A, "password": "wrong-password"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@test.syndi", "password": PASSWORD},
        )
        assert resp.status_code == 401


class TestToken:
    async def test_token_is_valid_jwt(self, client: AsyncClient):
        resp = await _register(client, EMAIL_B)
        assert resp.status_code == 200
        token = resp.json()["token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == EMAIL_B
        assert "exp" in payload


class TestProtected:
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        # /api/v1/auth/me использует Depends(get_current_user) —
        # без Bearer должен вернуть 401.
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_protected_endpoint_with_token(self, client: AsyncClient):
        reg = await _register(client, EMAIL_A, name="Alpha")
        token = reg.json()["token"]
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["email"] == EMAIL_A
