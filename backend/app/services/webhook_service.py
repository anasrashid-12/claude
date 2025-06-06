from typing import Dict, Any
import httpx
from ..models import Shop
from .shop_service import ShopService

class WebhookService:
    def __init__(self):
        self.shop_service = ShopService()
        
    async def handle_product_create(self, shop_domain: str, data: Dict[Any, Any]):
        """Handle product creation webhook"""
        shop = await self.shop_service.get_shop_by_url(shop_domain)
        if not shop:
            return
            
        # Extract product images and create processing jobs if auto-processing is enabled
        if shop.settings.get("auto_process_new_products", False):
            # Implementation for auto-processing new product images
            pass

    async def handle_product_update(self, shop_domain: str, data: Dict[Any, Any]):
        """Handle product update webhook"""
        shop = await self.shop_service.get_shop_by_url(shop_domain)
        if not shop:
            return
            
        # Handle product updates if needed
        pass

    async def handle_product_delete(self, shop_domain: str, data: Dict[Any, Any]):
        """Handle product deletion webhook"""
        # Clean up any processed images if needed
        pass

    async def handle_app_uninstalled(self, shop_domain: str):
        """Handle app uninstallation"""
        shop = await self.shop_service.get_shop_by_url(shop_domain)
        if shop:
            await self.shop_service.delete_shop(shop.id)

    async def register_shop_webhooks(self, shop_domain: str, access_token: str):
        """Register all required webhooks for a shop"""
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        webhooks = [
            {
                "topic": "products/create",
                "address": f"https://your-app-domain/api/v1/webhooks/shopify",
                "format": "json"
            },
            {
                "topic": "products/update",
                "address": f"https://your-app-domain/api/v1/webhooks/shopify",
                "format": "json"
            },
            {
                "topic": "products/delete",
                "address": f"https://your-app-domain/api/v1/webhooks/shopify",
                "format": "json"
            },
            {
                "topic": "app/uninstalled",
                "address": f"https://your-app-domain/api/v1/webhooks/shopify",
                "format": "json"
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for webhook in webhooks:
                try:
                    response = await client.post(
                        f"https://{shop_domain}/admin/api/2024-01/webhooks.json",
                        headers=headers,
                        json={"webhook": webhook}
                    )
                    response.raise_for_status()
                except Exception as e:
                    print(f"Error registering webhook {webhook['topic']}: {str(e)}")
                    # Continue with other webhooks even if one fails 