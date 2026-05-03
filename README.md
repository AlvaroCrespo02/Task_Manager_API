# Task Manager API

A full-stack task management application built with FastAPI. Users can register, log in, and manage their personal task lists through both a REST API and a server-rendered web interface.

Right now the frontend is being developed and functionality might be limited.

Check the [Live API](https://task-manager-api-28u8.onrender.com/) or the [docs](https://task-manager-api-28u8.onrender.com/docs)

## Features

- User registration and authentication with JWT tokens
- Create, read, update, and delete tasks
- Assign due dates and mark tasks as done
- Public user profiles and per-user task listings
- Server-rendered frontend via Jinja2 templates (currently being worked on)

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (production), SQLite (tests) |
| ORM | SQLAlchemy 2.0 (async) |
| DB Driver | asyncpg |
| Validation | Pydantic v2 |
| Authentication | JWT (PyJWT) + Argon2 password hashing (pwdlib) |
| Frontend | Jinja2 templates |
| Server | Uvicorn |
| Testing | pytest, pytest-asyncio, httpx |
| CI/CD | GitHub Actions |
| Deployment | Render |

## API Endpoints

### Users
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/users` | No | Register a new user |
| `POST` | `/api/users/token` | No | Log in, receive JWT token |
| `GET` | `/api/users/me` | Yes | Get current user info |
| `GET` | `/api/users/{id}` | No | Get public user profile |
| `PATCH` | `/api/users/{id}` | Yes | Update own account |
| `DELETE` | `/api/users/{id}` | Yes | Delete own account |
| `GET` | `/api/users/{id}/tasks` | No | Get all tasks for a user |

### Tasks
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/tasks` | No | List all tasks |
| `POST` | `/api/tasks` | Yes | Create a task |
| `GET` | `/api/tasks/{id}` | No | Get a specific task |
| `PUT` | `/api/tasks/{id}` | Yes | Full update of a task |
| `PATCH` | `/api/tasks/{id}` | Yes | Partial update of a task |
| `DELETE` | `/api/tasks/{id}` | Yes | Delete a task |

## Local Setup

### Prerequisites
- Python 3.12+
- PostgreSQL

### Installation

1. Clone the repository:

2. Install dependencies (requirements.txt):

3. Create a `.env` file in the project root:
    ```env
    SECRET_KEY=your-secret-key-at-least-32-characters-long
    DATABASE_URL=postgresql://user:password@localhost:5432/taskmanager
    ```


## CI/CD

Push or pull requests to `main` trigger a GitHub Actions workflow that:

1. Runs the full test suite
2. If tests pass and the event is a push to `main`, deploys to Render via a deploy hook
