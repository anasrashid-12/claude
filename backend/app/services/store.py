from typing import Optional, List
import shopify
from app.core.config import settings
from app.core.database import Database
from app.models.store import Store, StoreCreate, StoreUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StoreService:
    def __init__(self):
        self.db = Database()
        shopify.Session.setup(
            api_key=settings.SHOPIFY_API_KEY,
            secret=settings.SHOPIFY_API_SECRET
        )

    async def create_store(self, store_data: StoreCreate) -> Store:
        """
        Create a new store
        """
        try:
            result = await self.db.create("stores", store_data.model_dump())
            return Store(**result)
        except Exception as e:
            logger.error(f"Failed to create store: {e}")
            raise

    async def get_store(self, shop_domain: str) -> Optional[Store]:
        """
        Get a store by domain
        """
        try:
            result = await self.db.execute_query(
                "stores",
                lambda q: q.select("*").eq("shop_domain", shop_domain).single()
            )
            return Store(**result.data) if result.data else None
        except Exception as e:
            logger.error(f"Failed to get store: {e}")
            raise

    async def update_store(self, shop_domain: str, store_data: StoreUpdate) -> Optional[Store]:
        """
        Update a store
        """
        try:
            result = await self.db.execute_query(
                "stores",
                lambda q: q.update(store_data.model_dump(exclude_unset=True))
                    .eq("shop_domain", shop_domain)
                    .single()
            )
            return Store(**result.data) if result.data else None
        except Exception as e:
            logger.error(f"Failed to update store: {e}")
            raise

    async def delete_store(self, shop_domain: str) -> bool:
        """
        Delete a store
        """
        try:
            result = await self.db.execute_query(
                "stores",
                lambda q: q.delete().eq("shop_domain", shop_domain)
            )
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to delete store: {e}")
            raise

    async def list_stores(self, limit: int = 10, offset: int = 0) -> List[Store]:
        """
        List all stores
        """
        try:
            result = await self.db.execute_query(
                "stores",
                lambda q: q.select("*")
                    .order("created_at", desc=True)
                    .range(offset, offset + limit - 1)
            )
            return [Store(**store) for store in result.data]
        except Exception as e:
            logger.error(f"Failed to list stores: {e}")
            raise

    def create_shopify_session(self, shop_domain: str, access_token: str) -> shopify.Session:
        """
        Create a Shopify session
        """
        return shopify.Session(
            shop_domain,
            settings.SHOPIFY_API_VERSION,
            access_token
        )

    async def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """
        Verify Shopify webhook
        """
        from app.core.security import verify_shopify_webhook
        return verify_shopify_webhook(headers, body, settings.SHOPIFY_API_SECRET)

store_service = StoreService() 