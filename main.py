from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import TaskCreate, TaskResponse
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Task
from datetime import date

app = FastAPI()
Base.metadata.create_all(engine)
templates = Jinja2Templates(directory="templates")

# Mock data
tasks: list[dict] = [
    {
        "id": 1, 
        "task":'Buy groceries', 
        "created":'2026-02-26', 
        "due":'2026-03-26', 
        "done":True
    },
    {
        "id": 2, 
        "task":'Cook lunch', 
        "created":'2026-01-26', 
        "due":'2026-01-26', 
        "done":False
    },
]

# ENDPOINTS

@app.get("/", include_in_schema=False)
def root(request: Request):
    return templates.TemplateResponse(request, 
                                      "index.html", 
                                      {"title": "Home"})

@app.get("/tasks")
def task_page(request: Request):
    return templates.TemplateResponse(request, 
                                      "tasks.html", 
                                      {"tasks": tasks, "title": "Tasks"})

@app.get("/tasks/{task_id}")
def list_tasks(request: Request, task_id: int):
    for task in tasks:
        if task.get("id") == task_id:
            return templates.TemplateResponse(request, 
                                      "detailedTask.html", 
                                      {"task": task, "title": task["task"]}
                                      )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post was not found"
        )

@app.get("/api/dbhealth")
def check_db(db: Session = Depends(get_db)):
    return {"status": "db connection OK"}

@app.get("/api/tasks", response_model=list[TaskResponse])
def listTasks(db: Session = Depends(get_db)):
    taskList = db.query(Task).all()
    return taskList

@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session= Depends(get_db)):
    new_task = Task(
        task = task.task,
        created = date.today(),
        due = task.due,
        done = task.done
    )
    db.add(new_task)
    db.commit()
    return new_task

@app.get("/api/tasks/{task_id}/delete", status_code=status.HTTP_200_OK)
def deleteTask(task_id: int, db: Session = Depends(get_db)):
    print("Task ID: ", task_id)
    myTask = db.query(Task).get(task_id)
    if myTask is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(myTask)
    db.commit()
    return {"Message": "Entry deleted"}
    

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

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