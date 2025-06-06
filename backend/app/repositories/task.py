from typing import Dict, Any, Optional, List
from app.models.task import Task, TaskStatus, TaskType
from app.core.database import get_db

class TaskRepository:
    def __init__(self):
        self.db = get_db()

    def create(
        self,
        task_id: str,
        task_type: TaskType,
        store_id: int,
        status: TaskStatus,
        params: Dict[str, Any]
    ) -> Task:
        """Create a new task"""
        task = Task(
            id=task_id,
            task_type=task_type,
            store_id=store_id,
            status=status,
            params=params
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list_by_store(
        self,
        store_id: int,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a store"""
        query = self.db.query(Task).filter(Task.store_id == store_id)
        if status:
            query = query.filter(Task.status == status)
        return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    def update(
        self,
        task_id: str,
        status: TaskStatus,
        result: Dict[str, Any] = None,
        error_message: str = None
    ) -> Task:
        """Update task status"""
        task = self.get(task_id)
        if task:
            task.status = status
            if result is not None:
                task.result = result
            if error_message is not None:
                task.error_message = error_message
            self.db.commit()
            self.db.refresh(task)
        return task

task_repository = TaskRepository() 