from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum
from datetime import datetime
import uuid

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, enum.Enum):
    IMAGE_PROCESSING = "image_processing"
    BACKGROUND_REMOVAL = "background_removal"
    BULK_PROCESSING = "bulk_processing"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    progress = Column(Integer, default=0)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    store_id = Column(UUID(as_uuid=True), nullable=False)
    celery_task_id = Column(String, nullable=True)
    task_metadata = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "type": self.type.value,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "store_id": str(self.store_id),
            "celery_task_id": self.celery_task_id,
            "metadata": self.task_metadata
        }

    def __repr__(self):
        return f"<Task {self.id} ({self.type}: {self.status})>" 