from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from app.services.store import store_service
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

class InstallResponse(BaseModel):
    auth_url: str

class TokenResponse(BaseModel):
    access_token: str
    shop_domain: str

@router.get("/install")
async def install(shop: str, request: Request) -> InstallResponse:
    """
    Start Shopify OAuth installation process
    """
    try:
        # Build the OAuth URL
        redirect_uri = str(request.base_url)[:-1] + router.url_path_for("callback")
        auth_url = store_service.build_auth_url(shop, redirect_uri)
        return InstallResponse(auth_url=auth_url)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback")
async def callback(
    shop: str,
    code: str,
    hmac: Optional[str] = None,
    timestamp: Optional[str] = None,
    state: Optional[str] = None
) -> TokenResponse:
    """
    Handle Shopify OAuth callback
    """
    try:
        # Validate HMAC if provided
        if hmac and timestamp:
            params = {
                "shop": shop,
                "code": code,
                "timestamp": timestamp,
                "state": state
            }
            if not store_service.validate_hmac(shop, hmac, params):
                raise AuthenticationError("Invalid HMAC signature")

        # Exchange code for access token
        access_token = await store_service.exchange_code_for_token(shop, code)

        # Install or update store
        await store_service.install_store(shop, access_token)

        return TokenResponse(
            access_token=access_token,
            shop_domain=shop
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/uninstall")
async def uninstall(shop: str):
    """
    Uninstall app from a Shopify store
    """
    try:
        success = await store_service.uninstall_store(shop)
        if not success:
            raise HTTPException(status_code=404, detail="Store not found")
        return {"message": "Store uninstalled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 