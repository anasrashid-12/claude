from typing import List, Optional, Dict, Any
from app.models.task import Task, TaskStatus, TaskType
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        store_id: UUID,
        task_type: TaskType,
        celery_task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task"""
        try:
            task = Task(
                store_id=store_id,
                type=task_type,
                celery_task_id=celery_task_id,
                metadata=metadata
            )
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            self.db.rollback()
            raise

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def update_task(
        self,
        task_id: UUID,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Optional[Task]:
        """Update a task"""
        try:
            task = self.get_task(task_id)
            if not task:
                return None

            if status:
                task.status = status
            if progress is not None:
                task.progress = progress
            if result:
                task.result = result
            if error:
                task.error = error

            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            self.db.rollback()
            raise

    def list_tasks(
        self,
        store_id: UUID,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a store"""
        query = self.db.query(Task).filter(Task.store_id == store_id)
        
        if status:
            query = query.filter(Task.status == status)
            
        return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    def delete_task(self, task_id: UUID) -> bool:
        """Delete a task"""
        try:
            task = self.get_task(task_id)
            if not task:
                return False

            self.db.delete(task)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            self.db.rollback()
            raise

# Create a global instance of TaskService with a database session
task_service = TaskService(SessionLocal()) 