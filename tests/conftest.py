import os

# Must be set before any project imports so database.py creates a SQLite engine
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
# Provide a fallback so tests run in CI without a .env file
os.environ.setdefault("SECRET_KEY", "ci-test-only-key-not-used-in-production-abc")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, AsyncSessionLocal, Base, get_db
from main import app
from auth import hash_password
from models import User, Task


async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def reset_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user2(db_session: AsyncSession):
    user = User(
        username="testuser2",
        email="test2@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/users/token",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest_asyncio.fixture
async def auth_headers2(client: AsyncClient, test_user2: User):
    response = await client.post(
        "/api/users/token",
        data={"username": "test2@example.com", "password": "password123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest_asyncio.fixture
async def test_task(db_session: AsyncSession, test_user: User):
    task = Task(
        user_id=test_user.id,
        task="Test task",
        done=False,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
