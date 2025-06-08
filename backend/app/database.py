from typing import Dict, List, Optional
from supabase import create_client, Client
from .core.config import settings

class Database:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def get_store(self, shop_domain: str) -> Optional[Dict]:
        """Get store by domain."""
        response = await self.client.from_('stores').select('*').eq('domain', shop_domain).single().execute()
        return response.data if response.data else None

    async def create_store(self, shop_domain: str, access_token: str) -> Dict:
        """Create a new store."""
        store_data = {
            'domain': shop_domain,
            'access_token': access_token,
            'is_active': True
        }
        response = await self.client.from_('stores').insert(store_data).execute()
        return response.data[0]

    async def update_store(self, store_id: str, data: Dict) -> Dict:
        """Update store data."""
        response = await self.client.from_('stores').update(data).eq('id', store_id).execute()
        return response.data[0]

    async def get_products(self, store_id: str, page: int = 1, page_size: int = 20) -> List[Dict]:
        """Get products with pagination."""
        start = (page - 1) * page_size
        response = await self.client.from_('products')\
            .select('*')\
            .eq('store_id', store_id)\
            .range(start, start + page_size - 1)\
            .execute()
        return response.data

    async def upsert_product(self, product_data: Dict) -> Dict:
        """Create or update a product."""
        response = await self.client.from_('products')\
            .upsert(product_data, on_conflict='shopify_product_id')\
            .execute()
        return response.data[0]

    async def upsert_image(self, image_data: Dict) -> Dict:
        """Create or update an image."""
        response = await self.client.from_('images')\
            .upsert(image_data, on_conflict='shopify_image_id')\
            .execute()
        return response.data[0] 