from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
import hmac
import hashlib
import json
from typing import Optional
import httpx
from ...core.config import settings
from ...db.session import get_supabase_client
from ...models.store import Store
from ...utils.security import create_access_token

router = APIRouter()

def verify_shopify_hmac(request_params: dict, secret: str) -> bool:
    """Verify Shopify HMAC signature."""
    if 'hmac' not in request_params:
        return False
    
    hmac_value = request_params.pop('hmac')
    sorted_params = '&'.join([f"{key}={value}" for key, value in sorted(request_params.items())])
    
    calculated_hmac = hmac.new(
        secret.encode('utf-8'),
        sorted_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_hmac, hmac_value)

async def verify_shop_domain(shop_domain: str) -> bool:
    """Verify if the shop domain is a valid Shopify domain."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://{shop_domain}/admin/api/{settings.SHOPIFY_API_VERSION}/shop.json")
            return response.status_code == 401  # Will return 401 if shop exists but we're not authenticated
    except Exception:
        return False

@router.get("/install")
async def install(shop: str, request: Request):
    """Initialize Shopify OAuth installation."""
    if not await verify_shop_domain(shop):
        raise HTTPException(status_code=400, detail="Invalid Shopify shop domain")
    
    # Generate installation URL
    nonce = hashlib.sha256(shop.encode()).hexdigest()
    
    install_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={settings.SHOPIFY_API_KEY}&"
        f"scope={settings.SHOPIFY_SCOPES}&"
        f"redirect_uri={settings.SHOPIFY_APP_URL}/api/v1/auth/callback&"
        f"state={nonce}"
    )
    
    return RedirectResponse(url=install_url)

@router.get("/callback")
async def callback(
    shop: str,
    code: str,
    state: str,
    hmac: str,
    timestamp: str,
    supabase=Depends(get_supabase_client)
):
    """Handle Shopify OAuth callback."""
    # Verify HMAC
    params = {
        'shop': shop,
        'code': code,
        'state': state,
        'timestamp': timestamp,
        'hmac': hmac
    }
    
    if not verify_shopify_hmac(params, settings.SHOPIFY_API_SECRET):
        raise HTTPException(status_code=400, detail="Invalid HMAC signature")

    # Exchange temporary code for permanent access token
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{shop}/admin/oauth/access_token",
                json={
                    'client_id': settings.SHOPIFY_API_KEY,
                    'client_secret': settings.SHOPIFY_API_SECRET,
                    'code': code
                }
            )
            token_data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get access token: {str(e)}")

    # Get shop details
    try:
        async with httpx.AsyncClient() as client:
            headers = {'X-Shopify-Access-Token': token_data['access_token']}
            response = await client.get(
                f"https://{shop}/admin/api/{settings.SHOPIFY_API_VERSION}/shop.json",
                headers=headers
            )
            shop_data = response.json()['shop']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shop details: {str(e)}")

    # Store or update shop details in database
    store = Store(
        shop_domain=shop,
        access_token=token_data['access_token'],
        shop_name=shop_data['name'],
        email=shop_data['email'],
        country=shop_data.get('country', ''),
        currency=shop_data.get('currency', 'USD'),
        status='active'
    )

    try:
        result = await supabase.table('stores').upsert(store.dict()).execute()
        store_id = result.data[0]['id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save store details: {str(e)}")

    # Generate JWT for frontend
    access_token = create_access_token(
        data={
            "sub": str(store_id),
            "shop": shop,
            "scope": settings.SHOPIFY_SCOPES
        }
    )

    # Redirect to frontend with token
    return RedirectResponse(
        url=f"{settings.SHOPIFY_APP_URL}/auth/callback?token={access_token}&shop={shop}"
    ) 