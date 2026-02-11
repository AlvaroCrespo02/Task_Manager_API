from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Task, User
from database import get_db
from schemas import TaskResponse, UserCreate, UserPublic, UserPrivate, UserUpdate, Token

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func

from auth import create_access_token, hash_password, oauth2_scheme, verify_access_token, verify_password

from config import settings

router = APIRouter()
# USER ENDPOINTS

@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def api_create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
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
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
     form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
     db: Annotated[AsyncSession, Depends(get_db)]
    ):
    result = await db.execute(select(User).where(func.lower(User.email) == form_data.username.lower()))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    acces_token = create_access_token(data={"sub":str(user.id)}, expires_delta=access_token_expires)

    return Token(access_token=acces_token, token_type="bearer")

@router.get("/me", response_model=UserPrivate)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):

    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    
    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalars().first()
    if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    return user

# PARTIAL USER UPDATE
@router.patch("/{user_id}", response_model=UserPrivate)
async def api_update_user(user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_update.username is not None and user_update.username.lower() != user.username.lower():
         result = await db.execute(select(User).where(func.lower(User.username) == user_update.username.lower()))
         existing_user = result.scalars().first()
         if existing_user:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
         
    if user_update.email is not None and user_update.email.lower() != user.email.lower():
         result = await db.execute(select(User).where(func.lower(User.email) == user_update.email.lower()))
         existing_email = result.scalars().first()
         if existing_email:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    if user_update.username is not None:
         user.username = user_update.username
    if user_update.email is not None:
         user.email = user_update.email.lower()
    if user_update.image_file is not None:
         user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserPublic)
async def api_get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def api_get_user_tasks(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(select(Task).options(selectinload(Task.author)).where(Task.user_id == user_id))
    tasks = result.scalars().all()
    return tasks

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"Message": "User and tasks deleted"}