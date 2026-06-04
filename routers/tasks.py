from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Task, User
from database import get_db
from schemas import TaskCreate, TaskResponse, TaskUpdate

from auth import CurrentUser

from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# ============================================================
# Task ENDPOINTS
# ============================================================
# GET THE LIST OF TASKS
@router.get("")
async def list_tasks(request: Request):
    return templates.TemplateResponse(request, "error.html")

# CREATE A NEW TASK
@router.post("")
async def create_task(request: Request):
    return templates.TemplateResponse(request, "error.html")

# GET SPECIFIC TASK
@router.get("/{task_id}")
async def get_task(request: Request):
    return templates.TemplateResponse(request, "error.html")

# FULL TASK UPDATE
@router.put("/{task_id}")
async def update_task(request: Request):
    return templates.TemplateResponse(request, "error.html")

# PARTIAL TASK UPDATE
@router.patch("/{task_id}")
async def partial_update_task(request: Request):
    return templates.TemplateResponse(request, "error.html")
    
# DELETE TASK
@router.delete("/{task_id}")
async def delete_task(request: Request):
    return templates.TemplateResponse(request, "error.html")