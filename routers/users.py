from typing import Annotated

from fastapi.templating import Jinja2Templates

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Task, User
from database import get_db
from schemas import TaskResponse, UserCreate, UserPublic, UserPrivate, UserUpdate, Token

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func

from auth import create_access_token, hash_password, verify_password, CurrentUser

from config import settings

router = APIRouter()

templates = Jinja2Templates(directory="templates")
# ============================================================
# User ENDPOINTS
# ============================================================
# CREATE NEW USER
@router.post("/users")
async def create_user(request: Request):
    return templates.TemplateResponse(request, "error.html")

# LOGIN
@router.post("/users/token", response_model=Token)
async def login_for_access_token(request: Request):
    return templates.TemplateResponse(request, "error.html")

# PARTIAL USER UPDATE
@router.patch("/users/{user_id}")
async def update_user(request: Request):
    return templates.TemplateResponse(request, "error.html")

# GET USER INFO
@router.get("/users/{user_id}")
async def get_user(request: Request):
    return templates.TemplateResponse(request, "error.html")

# GET TASKS FOR A SPECIFIC USER
@router.get("/users/{user_id}/tasks")
async def get_user_tasks(request: Request):
    return templates.TemplateResponse(request, "error.html")

# DELETE USER
@router.delete("/users/{user_id}")
async def delete_user(request: Request):
    return templates.TemplateResponse(request, "error.html")