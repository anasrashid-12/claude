"""Shopify Client Module"""

import httpx
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ShopifyClient:
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.api_version = settings.SHOPIFY_API_VERSION
        self.base_url = f"https://{shop_domain}/admin/api/{self.api_version}"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """Make a request to Shopify API."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=json_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Shopify API request failed: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code if hasattr(e, 'response') else 500,
                detail=f"Shopify API request failed: {str(e)}"
            )

    async def get_products(
        self,
        limit: int = 50,
        page_info: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get products from Shopify."""
        params = {'limit': limit}
        if page_info:
            params['page_info'] = page_info
        if fields:
            params['fields'] = ','.join(fields)

        return await self._make_request('GET', 'products.json', params=params)

    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get a single product from Shopify."""
        return await self._make_request('GET', f'products/{product_id}.json')

    async def get_product_images(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all images for a product."""
        response = await self._make_request('GET', f'products/{product_id}/images.json')
        return response.get('images', [])

    async def get_product_image(self, product_id: str, image_id: str) -> Dict[str, Any]:
        """Get a single product image."""
        response = await self._make_request(
            'GET',
            f'products/{product_id}/images/{image_id}.json'
        )
        return response.get('image', {})

    async def update_product_image(
        self,
        product_id: str,
        image_id: str,
        image_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a product image."""
        return await self._make_request(
            'PUT',
            f'products/{product_id}/images/{image_id}.json',
            json_data={'image': image_data}
        )

    async def create_product_image(
        self,
        product_id: str,
        image_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new product image."""
        return await self._make_request(
            'POST',
            f'products/{product_id}/images.json',
            json_data={'image': image_data}
        )

    async def delete_product_image(self, product_id: str, image_id: str) -> None:
        """Delete a product image."""
        await self._make_request(
            'DELETE',
            f'products/{product_id}/images/{image_id}.json'
        ) 