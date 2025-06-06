from fastapi import Depends, Header, HTTPException
from app.services.store import store_service
from app.models.store import Store
from app.core.exceptions import AuthenticationError
from typing import Optional

async def get_current_store(
    x_shopify_shop_domain: Optional[str] = Header(None),
    x_shopify_access_token: Optional[str] = Header(None)
) -> Store:
    """
    Get current store from Shopify headers
    """
    if not x_shopify_shop_domain:
        raise HTTPException(
            status_code=401,
            detail="X-Shopify-Shop-Domain header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not x_shopify_access_token:
        raise HTTPException(
            status_code=401,
            detail="X-Shopify-Access-Token header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        store = await store_service.get_active_by_domain(x_shopify_shop_domain)
        if store.access_token != x_shopify_access_token:
            raise AuthenticationError("Invalid access token")
        return store
    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 