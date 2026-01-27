from sqlalchemy import Integer, String, Date, Boolean, Column
from database import Base

class Task(Base):
    __tablename__ = 'tasklist'
    id = Column(Integer, primary_key=True)
    task = Column(String, nullable=False)
    created = Column(Date, nullable=False)
    due = Column(Date, nullable=True)
    done = Column(Boolean, nullable=False)