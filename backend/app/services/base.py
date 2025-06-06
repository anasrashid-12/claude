from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from pydantic import BaseModel
from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundError, ValidationError

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(self, repository: Type[RepositoryType]):
        self.repository = repository()

    async def get(self, id: int) -> ModelType:
        """Get a record by ID"""
        result = await self.repository.get(id)
        if not result:
            raise NotFoundError(f"Record with id {id} not found")
        return result

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[ModelType]:
        """Get a list of records"""
        return await self.repository.list(filters, skip, limit, order_by, order)

    async def create(self, data: CreateSchemaType) -> ModelType:
        """Create a new record"""
        try:
            return await self.repository.create(data)
        except Exception as e:
            raise ValidationError(f"Failed to create record: {str(e)}")

    async def update(self, id: int, data: UpdateSchemaType) -> ModelType:
        """Update a record"""
        if not await self.repository.get(id):
            raise NotFoundError(f"Record with id {id} not found")
        
        try:
            result = await self.repository.update(id, data)
            if not result:
                raise NotFoundError(f"Record with id {id} not found")
            return result
        except Exception as e:
            raise ValidationError(f"Failed to update record: {str(e)}")

    async def delete(self, id: int) -> bool:
        """Delete a record"""
        if not await self.repository.get(id):
            raise NotFoundError(f"Record with id {id} not found")
        return await self.repository.delete(id)

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records"""
        return await self.repository.count(filters) 