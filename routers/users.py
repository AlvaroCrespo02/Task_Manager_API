from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Task, User
from database import get_db
from schemas import TaskResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter()
# USER ENDPOINTS

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def api_create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    result = await db.execute(select(User).where(User.email == user.email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    new_user = User(
        username = user.username,
        email = user.email
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) #Not strictly neccessary
    return new_user


# PARTIAL USER UPDATE
@router.patch("/{user_id}", response_model=UserResponse)
async def api_update_user(user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_update.username is not None and user_update.username != user.username:
         result = await db.execute(select(User).where(User.username == user_update.username))
         existing_user = result.scalars().first()
         if existing_user:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
         
    if user_update.email is not None and user_update.email != user.email:
         result = await db.execute(select(User).where(User.email == user_update.email))
         existing_email = result.scalars().first()
         if existing_email:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    if user_update.username is not None:
         user.username = user_update.username
    if user_update.email is not None:
         user.email = user_update.email
    if user_update.image_file is not None:
         user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
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