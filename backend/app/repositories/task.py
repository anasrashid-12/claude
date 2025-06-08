from typing import Dict, Any, Optional, List
from app.models.task import Task, TaskStatus, TaskType
from app.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class TaskRepository:
    def __init__(self):
        self.get_session = get_async_session

    async def create(
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
        async for session in self.get_session():
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        async for session in self.get_session():
            result = await session.execute(
                select(Task).filter(Task.id == task_id)
            )
            return result.scalar_one_or_none()

    async def list_by_store(
        self,
        store_id: int,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a store"""
        query = select(Task).filter(Task.store_id == store_id)
        if status:
            query = query.filter(Task.status == status)
        query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
        
        async for session in self.get_session():
            result = await session.execute(query)
            return result.scalars().all()

    async def update(
        self,
        task_id: str,
        status: TaskStatus,
        result: Dict[str, Any] = None,
        error_message: str = None
    ) -> Task:
        """Update task status"""
        task = await self.get(task_id)
        if task:
            async for session in self.get_session():
                task.status = status
                if result is not None:
                    task.result = result
                if error_message is not None:
                    task.error_message = error_message
                await session.commit()
                await session.refresh(task)
                return task
        return None

task_repository = TaskRepository() 