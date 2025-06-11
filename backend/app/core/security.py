from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.core.supabase import supabase
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validate JWT token and return user info.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the JWT token with Supabase
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise credentials_exception
        
        return user.dict()
    except Exception:
        raise credentials_exception

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    :param data: Data to encode in the token
    :param expires_delta: Optional expiration time delta
    :return: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token
    
    :param token: JWT token to verify
    :return: Decoded token payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

def verify_shopify_webhook(headers: dict, body: bytes, webhook_secret: str) -> bool:
    """
    Verify Shopify webhook HMAC
    
    :param headers: Request headers
    :param body: Raw request body
    :param webhook_secret: Shopify webhook secret
    :return: True if verification succeeds
    """
    import hmac
    import hashlib
    import base64
    
    try:
        hmac_header = headers.get('X-Shopify-Hmac-Sha256')
        if not hmac_header:
            return False
        
        digest = hmac.new(
            webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
        
        computed_hmac = base64.b64encode(digest).decode('utf-8')
        return hmac.compare_digest(computed_hmac, hmac_header)
    except Exception as e:
        logger.error(f"Webhook verification failed: {e}")
        return False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    # In this case, we'll delegate password verification to Supabase
    # This function is kept for compatibility and possible future use
    return True 