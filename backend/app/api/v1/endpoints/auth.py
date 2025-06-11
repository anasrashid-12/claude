from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.store import store_service
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.core.security import get_current_user, create_access_token, verify_token
from app.integrations.shopify import ShopifyAuth, ShopifyWebhooks
import logging

from app.core.supabase import supabase

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

class InstallResponse(BaseModel):
    auth_url: str

class TokenResponse(BaseModel):
    access_token: str
    shop_domain: str

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    store_url: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    store_url: Optional[str] = None

@router.get("/install")
async def install_app(shop: str):
    """Start Shopify OAuth process."""
    try:
        # Initialize auth
        auth = ShopifyAuth()
        
        # Verify shop domain
        if not await auth.verify_shop_domain(shop):
            raise HTTPException(status_code=400, detail="Invalid Shopify shop domain")
        
        # Create installation URL
        install_url = auth.create_install_url(shop)
        return {"auth_url": install_url}
        
    except Exception as e:
        logger.error(f"Failed to create install URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def oauth_callback(code: str, shop: str, state: Optional[str] = None):
    """Handle Shopify OAuth callback."""
    try:
        # Initialize auth
        auth = ShopifyAuth()
        
        # Exchange code for access token
        access_token = await auth.get_access_token(shop, code)
        
        # Get shop details
        shop_data = await auth.get_shop_data(shop, access_token)
        
        # Create store model
        store_model = auth.create_store_model(shop, access_token, shop_data)
        
        # Create or update store in database
        existing_store = await store_service.get_store(shop)
        if existing_store:
            store = await store_service.update_store(
                shop,
                {"access_token": access_token, "uninstalled_at": None}
            )
        else:
            store = await store_service.create_store(store_model)
        
        # Register webhooks
        webhooks = ShopifyWebhooks(shop, access_token)
        await webhooks.register_webhooks()
        
        # Create JWT token
        token = create_access_token({"store_id": str(store.id)})
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.SHOPIFY_APP_URL}/auth/callback?token={token}&shop={shop}"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/uninstall")
async def uninstall_webhook(request: Request):
    """Handle app uninstallation webhook."""
    try:
        # Get HMAC header
        hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
        if not hmac_header:
            raise HTTPException(status_code=401, detail="Missing HMAC header")
        
        # Get shop domain
        shop_domain = request.headers.get('X-Shopify-Shop-Domain')
        if not shop_domain:
            raise HTTPException(status_code=401, detail="Missing shop domain")
        
        # Get request body
        body = await request.body()
        
        # Verify webhook
        auth = ShopifyAuth()
        if not auth.verify_webhook(hmac_header, body):
            raise HTTPException(status_code=401, detail="Invalid HMAC signature")
        
        # Update store status
        store = await store_service.get_store(shop_domain)
        if store:
            await store_service.update_store(
                shop_domain,
                {"uninstalled_at": "now()"}
            )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Uninstall webhook failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify")
async def verify_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token and return store information
    """
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        store_id = token_data.get("store_id")
        
        if not store_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get store
        store = await store_service.get_store_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
            
        return store
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signup", response_model=Token)
async def signup(user_in: UserSignUp):
    """
    Sign up a new user.
    """
    try:
        # Create user in Supabase
        auth_response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
            "options": {
                "data": {
                    "store_url": user_in.store_url
                }
            }
        })
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    """
    Login existing user.
    """
    try:
        # Sign in user with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_in.email,
            "password": user_in.password
        })
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user.
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user info.
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "store_url": current_user.get("user_metadata", {}).get("store_url")
    } 