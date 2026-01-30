from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates

app = FastAPI()
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

@app.get("/", include_in_schema=False)
def root(request: Request):
    return templates.TemplateResponse(request, 
                                      "index.html", 
                                      {"title": "Home"})

@app.get("/tests")
def taskList(request: Request):
    return templates.TemplateResponse(request, 
                                      "tests.html", 
                                      {"tasks": tasks, "title": "Tests"})

@app.get("/tests/{task_id}")
def get_task(request: Request, task_id: int):
    for task in tasks:
        if task.get("id") == task_id:
            return templates.TemplateResponse(request, 
                                      "detailedTask.html", 
                                      {"task": task, "title": "Details"})
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post was not found"
        )
