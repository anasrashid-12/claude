from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from app.services.store import store_service
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.core.supabase import supabase
from app.core.security import get_current_user

router = APIRouter()

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