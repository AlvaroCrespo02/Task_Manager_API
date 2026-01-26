from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from models import Task


load_dotenv()
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_url = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
# postgresql://username:password@host:port/database_name

# engine = create_engine(db_url, echo=True)
engine = create_engine(db_url)

def dbHealthCheck():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print("Connected succesfully!")
            print(f"PostgreSQL version: {result.fetchone()[0]}")
    except Exception as e:
        print(f"Connection failed: {e}")

    engine.dispose()
    print("Engine disposed, all connections closed")

def checkList():
    taskList = []
    try:
        with engine.connect() as conn:
            query = conn.execute(text("SELECT * FROM tasklist"))
            for row in query.fetchall():
                task = {
                    "Task" : row[0],
                    "Created" : row[1],
                    "Due" : row[2],
                    "Done" : row[3]
                }
                taskList.append(task)
            # conn.commit() ONLY WHEN MAKING CHANGES
    except Exception as e:
        print(f"Connection failed: {e}")

    engine.dispose()
    print("Engine disposed, all connections closed")
    print(taskList)
    return taskList

def addTask(task):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
            INSERT INTO tasklist (task, created, due, done) VALUES
            (:title, :created, :due, :done);"""),
            {'title': task.title,
             'created': task.created,
             'due': task.due,
             'done': task.done})
            conn.commit()
            print("Task added succesfully")
    except Exception as e:
        print(f"Connection failed: {e}")
    return 0

def removeTask(task):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
            DELETE FROM tasklist WHERE id = :id"""),
            {'id': task.id})
            conn.commit()
            print("Task removed succesfully")
    except Exception as e:
        print(f"Connection failed: {e}")
    return 0


# newTask = Task(0, "Finish the API", "2026-01-26", "2026-02-28", "FALSE")
# addTask(newTask)

# badTask = Task(4, "Finish the API", "2026-01-26", "2026-02-28", "FALSE")
# removeTask(badTask)