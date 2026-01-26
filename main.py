from fastapi import FastAPI
import db_test

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    db_test.dbHealthCheck()
    return {"status": "healthy"}

@app.get("/tasks")
def listTasks():
    taskList = db_test.checkList()
    print("List of cars: ", taskList)
    # return {"task status": "finished"}
    return taskList

# Now I have to add functionalities to add and delete objects from the DB