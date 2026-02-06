from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from schemas import TaskCreate, TaskResponse, TaskUpdate, UserCreate, UserResponse, UserUpdate

from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import Base, engine, get_db
from models import Task, User
from datetime import date

from routers import tasks, users

# Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
         await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

# USER ENDPOINTS

@app.get("/users/{user_id}/tasks", include_in_schema=False, name="user_tasks")
async def user_task_list(request: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    result = await db.execute(select(Task).options(selectinload(Task.author)).where(Task.user_id == user_id))
    tasks = result.scalars().all()
    return templates.TemplateResponse(
        request, "tasks.html",
        {"tasks": tasks, "user": user, "title": f"{user.username}'s Tasks"}
    )


# TASK ENDPOINTS

@app.get("/", include_in_schema=False, name="root")
async def root(request: Request):
    return templates.TemplateResponse(request, 
                                      "index.html", 
                                      {"title": "Home"})

@app.get("/tasks", include_in_schema=False, response_model=list[TaskResponse])
async def list_tasks(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).options(selectinload(Task.author)), )
    tasks = result.scalars().all()
    return templates.TemplateResponse(request, 
                                      "tasks.html", 
                                      {"tasks":tasks, "title": "Home"})

@app.get("/tasks/{task_id}", include_in_schema=False)
async def list_tasks(request: Request, task_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).options(selectinload(Task.author)).where(Task.id == task_id))
    task = result.scalars().first()
    if task:
            title = task.task[:50]
            return templates.TemplateResponse(request, 
                                      "detailedTask.html", 
                                      {"task": task, "title": title}
                                      )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


# This deals with the Starlette exceptions
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    # If the url starts with /api we return a JSON response with the exception
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    # If it's not an API url we return the template with the exception
    # Build the message if it has specific details
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your equest and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code 
        # This makes sure we get the correct HTTP status code
        # otherwise we would get a 200 response
    )

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    # If the url starts with /api we return a JSON response with the exception
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
    # If it's not an API url we return the template with the exception
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        # This makes sure we get the correct HTTP status code
        # otherwise we would get a 200 response
    )