import pytest
from httpx import AsyncClient


class TestCreateUser:
    async def test_create_user_success(self, client: AsyncClient):
        response = await client.post(
            "/api/users",
            json={"username": "newuser", "email": "new@example.com", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    async def test_create_user_email_lowercased(self, client: AsyncClient):
        response = await client.post(
            "/api/users",
            json={"username": "newuser", "email": "New@Example.COM", "password": "password123"},
        )
        assert response.status_code == 201
        assert response.json()["email"] == "new@example.com"

    async def test_create_user_duplicate_username(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/users",
            json={"username": "testuser", "email": "other@example.com", "password": "password123"},
        )
        assert response.status_code == 400

    async def test_create_user_duplicate_username_case_insensitive(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/users",
            json={"username": "TESTUSER", "email": "other@example.com", "password": "password123"},
        )
        assert response.status_code == 400

    async def test_create_user_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/users",
            json={"username": "otheruser", "email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 400

    async def test_create_user_short_password(self, client: AsyncClient):
        response = await client.post(
            "/api/users",
            json={"username": "newuser", "email": "new@example.com", "password": "short"},
        )
        assert response.status_code == 422

    async def test_create_user_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/users",
            json={"username": "newuser", "email": "not-an-email", "password": "password123"},
        )
        assert response.status_code == 422

    async def test_create_user_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/users", json={"username": "newuser"})
        assert response.status_code == 422


class TestGetUser:
    async def test_get_user_public_info(self, client: AsyncClient, test_user):
        response = await client.get(f"/api/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert "email" not in data

    async def test_get_user_not_found(self, client: AsyncClient):
        response = await client.get("/api/users/99999")
        assert response.status_code == 404

    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        response = await client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_get_current_user_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/users/me")
        assert response.status_code == 401


class TestUpdateUser:
    async def test_update_own_username(self, client: AsyncClient, test_user, auth_headers):
        response = await client.patch(
            f"/api/users/{test_user.id}",
            json={"username": "updateduser"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "updateduser"

    async def test_update_own_email(self, client: AsyncClient, test_user, auth_headers):
        response = await client.patch(
            f"/api/users/{test_user.id}",
            json={"email": "updated@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["email"] == "updated@example.com"

    async def test_update_duplicate_username(self, client: AsyncClient, test_user, test_user2, auth_headers):
        response = await client.patch(
            f"/api/users/{test_user.id}",
            json={"username": "testuser2"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    async def test_update_same_username_allowed(self, client: AsyncClient, test_user, auth_headers):
        response = await client.patch(
            f"/api/users/{test_user.id}",
            json={"username": "testuser"},
            headers=auth_headers,
        )
        assert response.status_code == 200

    async def test_update_other_user_forbidden(self, client: AsyncClient, test_user2, auth_headers):
        response = await client.patch(
            f"/api/users/{test_user2.id}",
            json={"username": "hacked"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    async def test_update_user_unauthenticated(self, client: AsyncClient, test_user):
        response = await client.patch(
            f"/api/users/{test_user.id}",
            json={"username": "updated"},
        )
        assert response.status_code == 401


class TestDeleteUser:
    async def test_delete_own_user(self, client: AsyncClient, test_user, auth_headers):
        response = await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == 204

    async def test_delete_other_user_forbidden(self, client: AsyncClient, test_user2, auth_headers):
        response = await client.delete(f"/api/users/{test_user2.id}", headers=auth_headers)
        assert response.status_code == 403

    async def test_delete_user_unauthenticated(self, client: AsyncClient, test_user):
        response = await client.delete(f"/api/users/{test_user.id}")
        assert response.status_code == 401

    async def test_delete_user_cascades_tasks(self, client: AsyncClient, test_user, test_task, auth_headers):
        task_id = test_task.id
        await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)

        task_response = await client.get(f"/api/tasks/{task_id}")
        assert task_response.status_code == 404


class TestGetUserTasks:
    async def test_get_user_tasks(self, client: AsyncClient, test_user, test_task):
        response = await client.get(f"/api/users/{test_user.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["user_id"] == test_user.id
        assert data[0]["task"] == "Test task"

    async def test_get_user_tasks_empty(self, client: AsyncClient, test_user):
        response = await client.get(f"/api/users/{test_user.id}/tasks")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_tasks_for_nonexistent_user(self, client: AsyncClient):
        response = await client.get("/api/users/99999/tasks")
        assert response.status_code == 404
