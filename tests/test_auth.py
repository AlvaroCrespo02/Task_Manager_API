from datetime import timedelta

import pytest
from httpx import AsyncClient

from auth import create_access_token


class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/users/token",
            data={"username": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_case_insensitive_email(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/users/token",
            data={"username": "TEST@EXAMPLE.COM", "password": "password123"},
        )
        assert response.status_code == 200

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/users/token",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_email(self, client: AsyncClient):
        response = await client.post(
            "/api/users/token",
            data={"username": "nobody@example.com", "password": "password123"},
        )
        assert response.status_code == 401

    async def test_login_missing_password(self, client: AsyncClient):
        response = await client.post(
            "/api/users/token",
            data={"username": "test@example.com"},
        )
        assert response.status_code == 422

    async def test_login_missing_username(self, client: AsyncClient):
        response = await client.post(
            "/api/users/token",
            data={"password": "password123"},
        )
        assert response.status_code == 422


class TestTokenValidation:
    async def test_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer not.a.valid.token"},
        )
        assert response.status_code == 401

    async def test_malformed_bearer(self, client: AsyncClient):
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": "NotBearer sometoken"},
        )
        assert response.status_code == 401

    async def test_missing_token(self, client: AsyncClient):
        response = await client.get("/api/users/me")
        assert response.status_code == 401

    async def test_expired_token(self, client: AsyncClient, test_user):
        token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1),
        )
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
