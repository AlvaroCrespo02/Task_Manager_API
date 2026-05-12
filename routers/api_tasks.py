from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Task, User
from database import get_db
from schemas import TaskCreate, TaskResponse, TaskUpdate

from auth import CurrentUser

router = APIRouter()
# ============================================================
# Task ENDPOINTS
# ============================================================
# GET THE LIST OF TASKS
@router.get("", response_model=list[TaskResponse])
async def api_list_tasks(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).options(selectinload(Task.author)))
    tasks = result.scalars().all()
    return tasks

# CREATE A NEW TASK
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def api_create_task(task: TaskCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    
    new_task = Task(
        task = task.task,
        due = task.due,
        done = task.done,
        user_id = current_user.id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task, attribute_names=["author"])
    return new_task

# GET SPECIFIC TASK
@router.get("/{task_id}", response_model=TaskResponse)
async def api_get_task(task_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).options(selectinload(Task.author)).where(Task.id == task_id))
    task = result.scalars().first()
    if task:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

# FULL TASK UPDATE
@router.put("/{task_id}", response_model=TaskResponse)
async def api_update_task(task_id: int, task_data: TaskCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).options(selectinload(Task.author)).where(Task.id == task_id))
    task = result.scalars().first()

    if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    task.task = task_data.task
    task.due = task_data.due
    task.done = task_data.done

    await db.commit()
    await db.refresh(task, attribute_names=["author"]) #This does a refresh and loads the author relatioship
    return task

# PARTIAL TASK UPDATE
@router.patch("/{task_id}", response_model=TaskResponse)
async def api_partial_update_task(task_id: int, task_data: TaskUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    update_data = task_data.model_dump(exclude_unset=True) # This takes ONLY the fields that have content
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task, attribute_names=["author"])
    return task
    
# DELETE TASK
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_task(task_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    await db.delete(task)
    await db.commit()
    return {"Message": "Entry deleted"}