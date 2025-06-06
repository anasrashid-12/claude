from enum import Enum
from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base

class TaskType(str, Enum):
    IMAGE_PROCESSING = "image_processing"
    BULK_PROCESSING = "bulk_processing"

class TaskStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)  # Celery task ID
    store_id = Column(Integer, nullable=False)
    task_type = Column(SQLEnum(TaskType), nullable=False)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    params = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Task {self.id} ({self.task_type}: {self.status})>" 