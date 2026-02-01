from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Integer, String, DateTime, Boolean, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    tasks: Mapped[list[Task]] = relationship(back_populates="author")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "static/profile_pics/default.jpg"

# class Task(Base):
#     __tablename__ = "tasklist"
#     id = Column(Integer, primary_key=True)
#     task = Column(String, nullable=False)
#     created = Column(DateTime, nullable=False)
#     due = Column(DateTime, nullable=True)
#     done = Column(Boolean, nullable=False)

# Updated to 2.0 style declarative (SQLAlchemy 2.0+)
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_id"), nullable=False, index=True)
    task: Mapped[str] = mapped_column(String(100), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    due: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    done: Mapped[Boolean] = mapped_column(Boolean, nullable=False)
    author: Mapped[User] = relationship(back_populates="tasks")