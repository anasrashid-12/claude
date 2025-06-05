from typing import Optional, Dict, List, Any, TypeVar, Generic
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

T = TypeVar('T')

class Database:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.client: Client = create_client(supabase_url, supabase_key)

    async def get_store(self, shop_domain: str) -> Optional[Dict[str, Any]]:
        """Get store by shop domain."""
        response = await self.client.table('stores').select('*').eq('shop_domain', shop_domain).single().execute()
        return response.data if response.data else None

    async def create_store(self, shop_domain: str, access_token: str) -> Dict[str, Any]:
        """Create a new store."""
        store_data = {
            'shop_domain': shop_domain,
            'access_token': access_token,
            'is_active': True
        }
        response = await self.client.table('stores').insert(store_data).execute()
        return response.data[0]

    async def update_store(self, store_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update store data."""
        response = await self.client.table('stores').update(data).eq('id', store_id).execute()
        return response.data[0]

    async def get_products(self, store_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get paginated products for a store."""
        start = (page - 1) * page_size
        response = await self.client.table('products')\
            .select('*')\
            .eq('store_id', store_id)\
            .range(start, start + page_size - 1)\
            .execute()
        
        count = await self.client.table('products')\
            .select('id', count='exact')\
            .eq('store_id', store_id)\
            .execute()
            
        return {
            'data': response.data,
            'count': count.count,
            'page': page,
            'pageSize': page_size,
            'hasMore': count.count > (start + page_size)
        }

    async def get_images(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all images for a product."""
        response = await self.client.table('images')\
            .select('*')\
            .eq('product_id', product_id)\
            .order('position')\
            .execute()
        return response.data

    async def create_processing_history(
        self,
        image_id: str,
        operation: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new processing history entry."""
        history_data = {
            'image_id': image_id,
            'operation': operation,
            'status': 'pending',
            'settings': settings
        }
        response = await self.client.table('processing_history').insert(history_data).execute()
        return response.data[0]

    async def update_processing_status(
        self,
        history_id: str,
        status: str,
        error_message: Optional[str] = None,
        backup_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update processing history status."""
        update_data = {
            'status': status,
            'completed_at': datetime.utcnow().isoformat() if status in ['completed', 'failed'] else None
        }
        
        if error_message is not None:
            update_data['error_message'] = error_message
        if backup_url is not None:
            update_data['backup_url'] = backup_url

        response = await self.client.table('processing_history')\
            .update(update_data)\
            .eq('id', history_id)\
            .execute()
        return response.data[0]

    async def create_image_version(
        self,
        image_id: str,
        storage_url: str,
        processing_history_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new image version."""
        # Get the latest version number for this image
        response = await self.client.table('image_versions')\
            .select('version_number')\
            .eq('image_id', image_id)\
            .order('version_number', desc=True)\
            .limit(1)\
            .execute()
        
        next_version = 1 if not response.data else response.data[0]['version_number'] + 1
        
        version_data = {
            'image_id': image_id,
            'version_number': next_version,
            'storage_url': storage_url,
            'processing_history_id': processing_history_id
        }
        
        response = await self.client.table('image_versions').insert(version_data).execute()
        return response.data[0]

    async def get_store_settings(self, store_id: str) -> Optional[Dict[str, Any]]:
        """Get store settings."""
        response = await self.client.table('store_settings')\
            .select('*')\
            .eq('store_id', store_id)\
            .single()\
            .execute()
        return response.data if response.data else None

    async def update_store_settings(
        self,
        store_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update store settings."""
        response = await self.client.table('store_settings')\
            .upsert({'store_id': store_id, **settings})\
            .execute()
        return response.data[0] 