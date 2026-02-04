from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import TaskCreate, TaskResponse, TaskUpdate, UserCreate, UserResponse

from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Task, User
from datetime import date

Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

# USER ENDPOINTS

@app.get("/users/{user_id}/tasks", include_in_schema=False, name="user_tasks")
def user_task_list(request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    result = db.execute(select(Task).where(Task.user_id == user_id))
    tasks = result.scalars().all()
    return templates.TemplateResponse(
        request, "tasks.html",
        {"tasks": tasks, "user": user, "title": f"{user.username}'s Tasks"}
    )

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def api_create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    result = db.execute(select(User).where(User.email == user.email))
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
    db.commit()
    db.refresh(new_user) #Not strictly neccessary

    return new_user

@app.delete("/api/user/{user_id}", status_code=status.HTTP_200_OK)
def api_delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"Message": "User deleted"}

@app.get("/api/users/{user_id}", response_model=UserResponse)
def api_get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@app.get("/api/users/{user_id}/tasks", response_model=list[TaskResponse])
def api_get_user_tasks(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = db.execute(select(Task).where(Task.user_id == user_id))
    tasks = result.scalars().all()
    return tasks


# TASK ENDPOINTS

@app.get("/", include_in_schema=False, name="root")
def root(request: Request):
    return templates.TemplateResponse(request, 
                                      "index.html", 
                                      {"title": "Home"})

@app.get("/tasks", include_in_schema=False, response_model=list[TaskResponse])
def list_tasks(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task))
    tasks = result.scalars().all()
    return templates.TemplateResponse(request, 
                                      "tasks.html", 
                                      {"tasks":tasks, "title": "Home"})

@app.get("/tasks/{task_id}", include_in_schema=False)
def list_tasks(request: Request, task_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if task:
            title = task.task[:50]
            return templates.TemplateResponse(request, 
                                      "detailedTask.html", 
                                      {"task": task, "title": title}
                                      )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

# GOTTA REMAKE THIS ONE SINCE IT BROKE DOWN
# @app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, include_in_schema=False)
# def delete_task(request: Request, task_id: int, db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(Task).where(Task.id == task_id))
#     task = result.scalars().first()
#     if not task:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
#     db.delete(task)
#     db.commit()
#     return templates.TemplateResponse(request,
#                                       "deletedTask.html",
#                                       {"task": task, "title": task.task}
#                                       )

@app.get("/api/dbhealth")
def api_check_db(db: Annotated[Session, Depends(get_db)]):
    return {"status": "db connection OK"}

@app.get("/api/tasks", response_model=list[TaskResponse])
def api_list_tasks(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks

@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def api_create_task(task: TaskCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == task.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    new_task = Task(
        task = task.task,
        due = task.due,
        done = task.done,
        user_id = user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def api_get_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if task:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

# FULL TASK UPDATE
@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def api_update_task(task_id: int, task_data: TaskCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task_data.user_id != task.user_id:
        result = db.execute(select(User).where(User.id == task_data.user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    task.task = task_data.task
    task.due = task_data.due
    task.done = task_data.done
    task.user_id = task_data.user_id

    db.commit()
    db.refresh(task)
    return task

# PARTIAL TASK UPDATE
@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def api_partial_update_task(task_id: int, task_data: TaskUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    update_data = task_data.model_dump(exclude_unset=True) # This takes ONLY the fields that have content
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task
    

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"Message": "Entry deleted"}

# This deals with the Starlette exceptions
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    # Build the message if it has specific details
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your equest and try again."
    )
    # If the url starts with /api we return a JSON response with the exception
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"Details": message}
        )
    # If it's not an API url we return the template with the exception
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
def validation_exception_handler(request: Request, exception: RequestValidationError):
    # If the url starts with /api we return a JSON response with the exception
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"Details": exception.errors()}
        )
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