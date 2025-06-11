"""Session Management Module"""

from typing import Optional, Dict
from fastapi import Request, HTTPException
from app.core.security import verify_token
from app.services.store import store_service
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.store_service = store_service

    async def get_current_session(self, request: Request) -> Dict:
        """Get current session from request."""
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify token
            payload = verify_token(token)
            store_id = payload.get('store_id')
            
            if not store_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload"
                )
            
            # Get store
            store = await self.store_service.get_store_by_id(store_id)
            if not store:
                raise HTTPException(
                    status_code=401,
                    detail="Store not found"
                )
            
            if store.uninstalled_at:
                raise HTTPException(
                    status_code=401,
                    detail="App has been uninstalled"
                )
            
            return {
                'store_id': store_id,
                'shop_domain': store.shop_domain,
                'access_token': store.access_token
            }
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

    async def validate_webhook_session(
        self,
        request: Request,
        hmac_header: Optional[str] = None
    ) -> Dict:
        """Validate webhook request session."""
        from app.integrations.shopify import ShopifyAuth
        
        # Get shop domain
        shop_domain = request.headers.get('X-Shopify-Shop-Domain')
        if not shop_domain:
            raise HTTPException(
                status_code=401,
                detail="Missing shop domain"
            )
        
        # Get HMAC if not provided
        if not hmac_header:
            hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
            if not hmac_header:
                raise HTTPException(
                    status_code=401,
                    detail="Missing HMAC header"
                )
        
        # Get request body
        body = await request.body()
        
        # Verify webhook
        auth = ShopifyAuth()
        if not auth.verify_webhook(hmac_header, body):
            raise HTTPException(
                status_code=401,
                detail="Invalid HMAC signature"
            )
        
        # Get store
        store = await self.store_service.get_store(shop_domain)
        if not store:
            raise HTTPException(
                status_code=404,
                detail="Store not found"
            )
        
        return {
            'store_id': str(store.id),
            'shop_domain': store.shop_domain,
            'access_token': store.access_token
        }

session_manager = SessionManager() 