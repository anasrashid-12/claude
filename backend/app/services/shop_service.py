from typing import Optional, List
from ..models import Shop
from ..core.database import get_supabase

class ShopService:
    def __init__(self):
        self.supabase = get_supabase()

    async def create_shop(self, shop: Shop) -> Shop:
        """Create a new shop"""
        response = self.supabase.table("shops").insert({
            "shop_url": shop.shop_url,
            "access_token": shop.access_token,
            "shop_name": shop.shop_name,
            "email": shop.email,
            "plan_name": shop.plan_name,
            "settings": shop.settings
        }).execute()
        
        return Shop(**response.data[0])

    async def get_shop(self, shop_id: str) -> Optional[Shop]:
        """Get shop by ID"""
        response = self.supabase.table("shops").select("*").eq("id", shop_id).execute()
        
        if not response.data:
            return None
            
        return Shop(**response.data[0])

    async def get_shop_by_url(self, shop_url: str) -> Optional[Shop]:
        """Get shop by URL"""
        response = self.supabase.table("shops").select("*").eq("shop_url", shop_url).execute()
        
        if not response.data:
            return None
            
        return Shop(**response.data[0])

    async def update_shop(self, shop_id: str, update_data: dict) -> Shop:
        """Update shop details"""
        response = self.supabase.table("shops").update(update_data).eq("id", shop_id).execute()
        
        if not response.data:
            raise ValueError(f"Shop with ID {shop_id} not found")
            
        return Shop(**response.data[0])

    async def delete_shop(self, shop_id: str):
        """Delete a shop"""
        self.supabase.table("shops").delete().eq("id", shop_id).execute()

    async def list_shops(self, limit: int = 50, offset: int = 0) -> List[Shop]:
        """List all shops"""
        response = self.supabase.table("shops").select("*").range(offset, offset + limit - 1).execute()
        
        return [Shop(**shop_data) for shop_data in response.data] 