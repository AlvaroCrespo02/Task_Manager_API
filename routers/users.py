from typing import Annotated

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

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
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    result = await db.execute(select(User).where(func.lower(User.username) == user.username.lower()))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    result = await db.execute(select(User).where(func.lower(User.email) == user.email.lower()))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    new_user = User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) #Not strictly neccessary
    return templates.TemplateResponse(
        request,
        "home.html",
        {"message": "User created successfully! You can now log in."},
        status_code=status.HTTP_201_CREATED)

# LOGIN
@router.post("/token", include_in_schema=False)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request
    ):
    result = await db.execute(select(User).where(func.lower(User.email) == form_data.username.lower()))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        return templates.TemplateResponse(request, "error.html", {"error":  "Incorrect email or password"}, status_code=status.HTTP_401_UNAUTHORIZED)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub":str(user.id)}, expires_delta=access_token_expires)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# LOGOUT
@router.post("/logout", include_in_schema=False)
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# PARTIAL USER UPDATE
@router.patch("/{user_id}")
async def update_user(request: Request):
    return templates.TemplateResponse(request, "error.html")

# GET USER INFO
@router.get("/{user_id}")
async def get_user(request: Request):
    return templates.TemplateResponse(request, "error.html")

# GET TASKS FOR A SPECIFIC USER
@router.get("/{user_id}/tasks")
async def get_user_tasks(request: Request):
    return templates.TemplateResponse(request, "error.html")

# DELETE USER
@router.delete("/{user_id}")
async def delete_user(request: Request):
    return templates.TemplateResponse(request, "error.html")