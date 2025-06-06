from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
from ....services.shop_service import ShopService
from ....services.webhook_service import WebhookService
from ....core.auth import verify_webhook_hmac

router = APIRouter()

@router.post("/shopify")
async def handle_shopify_webhook(
    request: Request,
    topic: Optional[str] = Header(None, alias="X-Shopify-Topic"),
    shop_domain: Optional[str] = Header(None, alias="X-Shopify-Shop-Domain"),
    hmac: Optional[str] = Header(None, alias="X-Shopify-Hmac-Sha256"),
    webhook_service: WebhookService = Depends(),
    shop_service: ShopService = Depends()
):
    """Handle incoming Shopify webhooks"""
    # Verify webhook authenticity
    if not await verify_webhook_hmac(request, hmac):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        # Get request body
        body = await request.json()
        
        # Process webhook based on topic
        if topic == "products/create":
            await webhook_service.handle_product_create(shop_domain, body)
        elif topic == "products/update":
            await webhook_service.handle_product_update(shop_domain, body)
        elif topic == "products/delete":
            await webhook_service.handle_product_delete(shop_domain, body)
        elif topic == "app/uninstalled":
            await webhook_service.handle_app_uninstalled(shop_domain)
        else:
            # Log unknown webhook topic
            print(f"Received unknown webhook topic: {topic}")
        
        return {"status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/shopify/register")
async def register_webhooks(
    shop_domain: str,
    access_token: str,
    webhook_service: WebhookService = Depends()
):
    """Register all required webhooks for a shop"""
    try:
        await webhook_service.register_shop_webhooks(shop_domain, access_token)
        return {"status": "success", "message": "Webhooks registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 