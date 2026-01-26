from sqlalchemy import create_engine, Integer, String, Date, Boolean, Float, Column, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from dotenv import load_dotenv
import os

load_dotenv()
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_url = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
# postgresql://username:password@host:port/database_name

Base = declarative_base()

# Define a Python class that maps to a database table
class Task(Base):
    __tablename__ = 'tasklist'
    id = Column(Integer, primary_key=True)
    task = Column(String, nullable=False)
    created = Column(Date, nullable=False)
    due = Column(Date, nullable=True)
    done = Column(Boolean, nullable=False)

# Create database connection
engine = create_engine(db_url)
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Work with objects
newTask = Task(task='Go to bed 2', created='2026-01-26', due='2026-01-26', done=False)
session.add(newTask)
session.commit()

# Query using Python syntax
result = session.query(Task).filter_by(task='Go to bed 2').first()
print("You registered the task: ", result.task)