from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Task

app = FastAPI()

Base.metadata.create_all(engine)

# newTask = Task(task='Go to bed 2', created='2026-01-26', due='2026-01-26', done=False)

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/health/db")
def check_db(db: Session = Depends(get_db)):
    # This means that FastAPI calls get_db() gets the return as db
    # then runs the function
    # db.execute('SELECT 1')
    return {"status": "db connection OK"}

@app.get("/tasks")
def listTasks(db: Session = Depends(get_db)):
    taskList = db.query(Task).all()
    return taskList
