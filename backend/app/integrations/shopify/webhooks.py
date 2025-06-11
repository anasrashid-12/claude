"""Shopify Webhooks Module"""

import httpx
from typing import Dict, List, Optional, Callable, Any
from fastapi import HTTPException
from app.core.config import settings
import logging
from .client import ShopifyClient

logger = logging.getLogger(__name__)

class ShopifyWebhooks:
    WEBHOOK_TOPICS = [
        'app/uninstalled',
        'products/create',
        'products/update',
        'products/delete',
        'shop/update'
    ]

    def __init__(self, shop_domain: str, access_token: str):
        self.client = ShopifyClient(shop_domain, access_token)
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.webhook_url = f"{settings.SHOPIFY_APP_URL}/api/v1/webhooks"

    async def register_webhooks(self) -> List[Dict[str, Any]]:
        """Register all required webhooks."""
        registered_webhooks = []
        
        for topic in self.WEBHOOK_TOPICS:
            try:
                webhook = await self._create_webhook(topic)
                registered_webhooks.append(webhook)
            except Exception as e:
                logger.error(f"Failed to register webhook for topic {topic}: {str(e)}")
                # Continue with other webhooks even if one fails
                continue
        
        return registered_webhooks

    async def _create_webhook(self, topic: str) -> Dict[str, Any]:
        """Create a single webhook."""
        webhook_data = {
            'webhook': {
                'topic': topic,
                'address': f"{self.webhook_url}/{topic}",
                'format': 'json'
            }
        }

        try:
            response = await self.client._make_request(
                'POST',
                'webhooks.json',
                json_data=webhook_data
            )
            return response['webhook']
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create webhook: {str(e)}"
            )

    async def delete_webhooks(self) -> None:
        """Delete all webhooks for the app."""
        try:
            webhooks = await self.client._make_request('GET', 'webhooks.json')
            for webhook in webhooks.get('webhooks', []):
                await self.client._make_request(
                    'DELETE',
                    f"webhooks/{webhook['id']}.json"
                )
        except Exception as e:
            logger.error(f"Failed to delete webhooks: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete webhooks: {str(e)}"
            )

    async def verify_webhook_request(self, hmac_header: str, body: bytes) -> bool:
        """Verify webhook request from Shopify."""
        from .auth import ShopifyAuth
        auth = ShopifyAuth()
        return auth.verify_webhook(hmac_header, body) 