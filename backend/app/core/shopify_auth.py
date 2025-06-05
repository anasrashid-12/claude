from fastapi import HTTPException, Request
import hmac
import hashlib
import json
from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SHOPIFY_APP_URL = os.getenv("SHOPIFY_APP_URL")

def verify_shopify_webhook(request: Request) -> bool:
    """Verify that the webhook request came from Shopify."""
    try:
        # Get the HMAC header
        hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
        if not hmac_header:
            return False

        # Calculate the HMAC
        digest = hmac.new(
            SHOPIFY_API_SECRET.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(digest, hmac_header)
    except Exception:
        return False

def verify_shopify_request(params: Dict[str, str]) -> bool:
    """Verify that the request came from Shopify."""
    try:
        # Remove the signature from the parameters
        hmac_value = params.pop('hmac', None)
        if not hmac_value:
            return False

        # Sort the parameters
        sorted_params = '&'.join([
            f"{key}={value}"
            for key, value in sorted(params.items())
        ])

        # Calculate the HMAC
        digest = hmac.new(
            SHOPIFY_API_SECRET.encode('utf-8'),
            sorted_params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(digest, hmac_value)
    except Exception:
        return False

def get_shopify_access_token(shop_domain: str, code: str) -> str:
    """Exchange the authorization code for an access token."""
    try:
        import requests

        # Prepare the request
        url = f"https://{shop_domain}/admin/oauth/access_token"
        data = {
            'client_id': SHOPIFY_API_KEY,
            'client_secret': SHOPIFY_API_SECRET,
            'code': code
        }

        # Make the request
        response = requests.post(url, json=data)
        response.raise_for_status()

        # Extract the access token
        return response.json()['access_token']
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get access token: {str(e)}"
        ) 