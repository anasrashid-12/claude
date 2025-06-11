"""Shopify Authentication Module"""

import hmac
import hashlib
import httpx
from typing import Dict, Optional
from fastapi import HTTPException
from app.core.config import settings
from app.models.store import Store, StoreCreate
from datetime import datetime

class ShopifyAuth:
    def __init__(self):
        self.api_key = settings.SHOPIFY_API_KEY
        self.api_secret = settings.SHOPIFY_API_SECRET
        self.app_url = settings.SHOPIFY_APP_URL
        self.api_version = settings.SHOPIFY_API_VERSION
        self.scopes = settings.SHOPIFY_SCOPES

    def create_install_url(self, shop_domain: str) -> str:
        """Create Shopify OAuth installation URL."""
        nonce = hashlib.sha256(shop_domain.encode()).hexdigest()
        
        return (
            f"https://{shop_domain}/admin/oauth/authorize?"
            f"client_id={self.api_key}&"
            f"scope={self.scopes}&"
            f"redirect_uri={self.app_url}/api/v1/auth/callback&"
            f"state={nonce}"
        )

    async def verify_shop_domain(self, shop_domain: str) -> bool:
        """Verify if the shop domain is a valid Shopify domain."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{shop_domain}/admin/api/{self.api_version}/shop.json"
                )
                return response.status_code == 401  # Will return 401 if shop exists but we're not authenticated
        except Exception:
            return False

    def verify_hmac(self, params: Dict[str, str]) -> bool:
        """Verify Shopify HMAC signature."""
        if 'hmac' not in params:
            return False
        
        hmac_value = params.pop('hmac')
        sorted_params = '&'.join([
            f"{key}={value}" 
            for key, value in sorted(params.items())
        ])
        
        calculated_hmac = hmac.new(
            self.api_secret.encode('utf-8'),
            sorted_params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_hmac, hmac_value)

    def verify_webhook(self, hmac_header: str, body: bytes) -> bool:
        """Verify Shopify webhook request."""
        calculated_hmac = hmac.new(
            self.api_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_hmac, hmac_header)

    async def get_access_token(self, shop_domain: str, code: str) -> str:
        """Exchange the authorization code for an access token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://{shop_domain}/admin/oauth/access_token",
                    json={
                        'client_id': self.api_key,
                        'client_secret': self.api_secret,
                        'code': code
                    }
                )
                response.raise_for_status()
                return response.json()['access_token']
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get access token: {str(e)}"
            )

    async def get_shop_data(self, shop_domain: str, access_token: str) -> Dict:
        """Get shop details using access token."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {'X-Shopify-Access-Token': access_token}
                response = await client.get(
                    f"https://{shop_domain}/admin/api/{self.api_version}/shop.json",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()['shop']
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get shop details: {str(e)}"
            )

    def create_store_model(self, shop_domain: str, access_token: str, shop_data: Dict) -> Store:
        """Create Store model from shop data."""
        return Store(
            shop_domain=shop_domain,
            access_token=access_token,
            shop_name=shop_data['name'],
            email=shop_data.get('email'),
            installed_at=datetime.utcnow()
        ) 