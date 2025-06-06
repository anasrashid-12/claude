from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from pydantic import BaseModel
from app.core.database import db

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], table_name: str):
        self.model = model
        self.table_name = table_name

    async def get(self, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        result = db.client.table(self.table_name).select("*").eq("id", id).execute()
        return self.model(**result.data[0]) if result.data else None

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field value"""
        result = db.client.table(self.table_name).select("*").eq(field, value).execute()
        return self.model(**result.data[0]) if result.data else None

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[ModelType]:
        """Get a list of records with optional filtering"""
        query = db.client.table(self.table_name).select("*")
        
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
        
        query = query.order(order_by, desc=(order.lower() == "desc"))
        query = query.range(skip, skip + limit - 1)
        
        result = query.execute()
        return [self.model(**item) for item in result.data]

    async def create(self, data: CreateSchemaType) -> ModelType:
        """Create a new record"""
        result = db.client.table(self.table_name).insert(data.model_dump()).execute()
        return self.model(**result.data[0])

    async def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        """Update a record"""
        result = db.client.table(self.table_name).update(
            data.model_dump(exclude_unset=True)
        ).eq("id", id).execute()
        return self.model(**result.data[0]) if result.data else None

    async def delete(self, id: int) -> bool:
        """Delete a record"""
        result = db.client.table(self.table_name).delete().eq("id", id).execute()
        return bool(result.data)

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        query = db.client.table(self.table_name).select("id", count="exact")
        
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
        
        result = query.execute()
        return result.count if result.count is not None else 0 