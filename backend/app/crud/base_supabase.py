from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from app.core.supabase import supabase

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], table_name: str):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.model = model
        self.table_name = table_name

    async def get(self, id: str) -> Optional[ModelType]:
        """
        Get a single record by ID.
        """
        response = supabase.table(self.table_name).select("*").eq("id", id).execute()
        data = response.data
        if not data:
            return None
        return self.model(**data[0])

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        """
        query = supabase.table(self.table_name).select("*")
        
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.eq(field, value)
        
        query = query.range(skip, skip + limit - 1)
        response = query.execute()
        
        return [self.model(**item) for item in response.data]

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        """
        obj_in_data = obj_in.model_dump()
        response = supabase.table(self.table_name).insert(obj_in_data).execute()
        return self.model(**response.data[0])

    async def update(
        self,
        *,
        id: str,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        response = supabase.table(self.table_name).update(update_data).eq("id", id).execute()
        return self.model(**response.data[0])

    async def remove(self, *, id: str) -> ModelType:
        """
        Delete a record.
        """
        response = supabase.table(self.table_name).delete().eq("id", id).execute()
        return self.model(**response.data[0])

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.
        """
        query = supabase.table(self.table_name).select("*", count="exact")
        
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query = query.eq(field, value)
        
        response = query.execute()
        return response.count 