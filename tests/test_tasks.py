import pytest
from httpx import AsyncClient


class TestGetTasks:
    async def test_get_all_tasks_empty(self, client: AsyncClient):
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_all_tasks(self, client: AsyncClient, test_task):
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["task"] == "Test task"

    async def test_get_task_by_id(self, client: AsyncClient, test_task):
        response = await client.get(f"/api/tasks/{test_task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["task"] == "Test task"
        assert data["done"] is False
        assert "author" in data
        assert "email" not in data["author"]

    async def test_get_task_not_found(self, client: AsyncClient):
        response = await client.get("/api/tasks/99999")
        assert response.status_code == 404


FUTURE_DUE = "2027-01-01T12:00:00"


class TestCreateTask:
    async def test_create_task_success(self, client: AsyncClient, test_user, auth_headers):
        response = await client.post(
            "/api/tasks",
            json={"task": "New task", "done": False, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["task"] == "New task"
        assert data["done"] is False
        assert data["user_id"] == test_user.id
        assert "author" in data
        assert data["author"]["username"] == "testuser"

    async def test_create_task_with_due_date(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/tasks",
            json={"task": "Task with due date", "done": False, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["due"] is not None

    async def test_create_task_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/tasks",
            json={"task": "New task", "done": False, "due": FUTURE_DUE},
        )
        assert response.status_code == 401

    async def test_create_task_empty_name(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/tasks",
            json={"task": "", "done": False, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_task_name_too_long(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/tasks",
            json={"task": "a" * 101, "done": False, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_task_missing_task_field(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/tasks",
            json={"done": False, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestFullUpdateTask:
    async def test_put_task_success(self, client: AsyncClient, test_task, auth_headers):
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"task": "Updated task", "done": True, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "Updated task"
        assert data["done"] is True

    async def test_put_task_forbidden(self, client: AsyncClient, test_task, auth_headers2):
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"task": "Hacked", "done": False, "due": FUTURE_DUE},
            headers=auth_headers2,
        )
        assert response.status_code == 403

    async def test_put_task_unauthenticated(self, client: AsyncClient, test_task):
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"task": "Updated", "done": False, "due": FUTURE_DUE},
        )
        assert response.status_code == 401

    async def test_put_task_not_found(self, client: AsyncClient, auth_headers):
        response = await client.put(
            "/api/tasks/99999",
            json={"task": "Updated", "done": False, "due": FUTURE_DUE},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestPartialUpdateTask:
    async def test_patch_task_done(self, client: AsyncClient, test_task, auth_headers):
        response = await client.patch(
            f"/api/tasks/{test_task.id}",
            json={"done": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["done"] is True
        assert response.json()["task"] == "Test task"

    async def test_patch_task_name(self, client: AsyncClient, test_task, auth_headers):
        response = await client.patch(
            f"/api/tasks/{test_task.id}",
            json={"task": "Renamed task"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["task"] == "Renamed task"

    async def test_patch_task_forbidden(self, client: AsyncClient, test_task, auth_headers2):
        response = await client.patch(
            f"/api/tasks/{test_task.id}",
            json={"done": True},
            headers=auth_headers2,
        )
        assert response.status_code == 403

    async def test_patch_task_unauthenticated(self, client: AsyncClient, test_task):
        response = await client.patch(
            f"/api/tasks/{test_task.id}",
            json={"done": True},
        )
        assert response.status_code == 401

    async def test_patch_task_not_found(self, client: AsyncClient, auth_headers):
        response = await client.patch(
            "/api/tasks/99999",
            json={"done": True},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteTask:
    async def test_delete_task_success(self, client: AsyncClient, test_task, auth_headers):
        response = await client.delete(f"/api/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == 204

        response = await client.get(f"/api/tasks/{test_task.id}")
        assert response.status_code == 404

    async def test_delete_task_forbidden(self, client: AsyncClient, test_task, auth_headers2):
        response = await client.delete(f"/api/tasks/{test_task.id}", headers=auth_headers2)
        assert response.status_code == 403

    async def test_delete_task_unauthenticated(self, client: AsyncClient, test_task):
        response = await client.delete(f"/api/tasks/{test_task.id}")
        assert response.status_code == 401

    async def test_delete_task_not_found(self, client: AsyncClient, auth_headers):
        response = await client.delete("/api/tasks/99999", headers=auth_headers)
        assert response.status_code == 404
