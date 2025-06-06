from typing import Dict, Any, Optional, List
from app.models.task import Task, TaskStatus, TaskType
from app.repositories.task import task_repository
from app.core.celery import celery_app

class TaskService:
    def __init__(self):
        self.repository = task_repository

    def create(
        self,
        task_id: str,
        task_type: TaskType,
        store_id: int,
        params: Dict[str, Any]
    ) -> Task:
        """Create a new task"""
        return self.repository.create(
            task_id=task_id,
            task_type=task_type,
            store_id=store_id,
            status=TaskStatus.PENDING,
            params=params
        )

    def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.repository.get(task_id)

    def list_by_store(
        self,
        store_id: int,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a store"""
        return self.repository.list_by_store(
            store_id=store_id,
            status=status,
            limit=limit,
            offset=offset
        )

    def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Dict[str, Any] = None,
        error_message: str = None
    ) -> Task:
        """Update task status"""
        return self.repository.update(
            task_id=task_id,
            status=status,
            result=result,
            error_message=error_message
        )

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status from Celery"""
        result = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.successful() else None,
            "error": str(result.result) if result.failed() else None
        }

    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """Revoke a running task"""
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            self.update_status(
                task_id=task_id,
                status=TaskStatus.REVOKED
            )
            return True
        except Exception:
            return False

task_service = TaskService() 