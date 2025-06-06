from typing import Optional
from app.models.store import Store, StoreCreate, StoreUpdate
from app.repositories.base import BaseRepository

class StoreRepository(BaseRepository[Store, StoreCreate, StoreUpdate]):
    def __init__(self):
        super().__init__(Store, "stores")

    async def get_by_domain(self, shop_domain: str) -> Optional[Store]:
        """Get a store by its domain"""
        return await self.get_by_field("shop_domain", shop_domain)

    async def get_active_by_domain(self, shop_domain: str) -> Optional[Store]:
        """Get an active store by its domain"""
        result = self.db.client.table(self.table_name)\
            .select("*")\
            .eq("shop_domain", shop_domain)\
            .eq("is_active", True)\
            .execute()
        return Store(**result.data[0]) if result.data else None

    async def deactivate(self, shop_domain: str) -> bool:
        """Deactivate a store"""
        result = self.db.client.table(self.table_name)\
            .update({"is_active": False})\
            .eq("shop_domain", shop_domain)\
            .execute()
        return bool(result.data)

    async def update_access_token(self, shop_domain: str, access_token: str) -> Optional[Store]:
        """Update store's access token"""
        result = self.db.client.table(self.table_name)\
            .update({"access_token": access_token})\
            .eq("shop_domain", shop_domain)\
            .execute()
        return Store(**result.data[0]) if result.data else None 