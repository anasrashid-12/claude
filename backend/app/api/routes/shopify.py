from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List
import shopify
from ...core.shopify_auth import verify_shopify_request, get_shopify_access_token
from ...core.rate_limiter import rate_limit_by_ip
from ...database import Database
from ...schemas.shopify import StoreAuth, ProductSync

router = APIRouter(prefix="/shopify", tags=["shopify"])
db = Database()

@router.get("/auth")
async def auth_callback(
    shop: str,
    code: str,
    state: str,
    request: Request,
    _rate_limit: None = Depends(rate_limit_by_ip)
):
    """Handle Shopify OAuth callback."""
    # Verify the request is from Shopify
    params = dict(request.query_params)
    if not verify_shopify_request(params):
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        # Exchange code for access token
        access_token = get_shopify_access_token(shop, code)

        # Store the shop details in database
        store = await db.get_store(shop)
        if store:
            await db.update_store(store['id'], {'access_token': access_token})
        else:
            store = await db.create_store(shop, access_token)

        return {
            "status": "success",
            "shop": shop,
            "store_id": store['id']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products")
async def get_products(
    shop: str,
    page: int = 1,
    page_size: int = 20,
    _rate_limit: None = Depends(rate_limit_by_ip)
):
    """Get products from a Shopify store."""
    try:
        # Get store from database
        store = await db.get_store(shop)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        # Get products with pagination
        products = await db.get_products(store['id'], page, page_size)
        return products
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sync/products")
async def sync_products(
    request: Request,
    sync_data: ProductSync,
    _rate_limit: None = Depends(rate_limit_by_ip)
):
    """Sync products from Shopify to our database."""
    try:
        # Get store from database
        store = await db.get_store(sync_data.shop)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        # Initialize Shopify session
        session = shopify.Session(sync_data.shop, '2024-01', store['access_token'])
        shopify.ShopifyResource.activate_session(session)

        # Get products from Shopify
        products = shopify.Product.find(limit=250)  # Maximum allowed by Shopify

        # Process each product
        for product in products:
            product_data = {
                'shopify_product_id': str(product.id),
                'title': product.title,
                'store_id': store['id']
            }
            
            # Create or update product in our database
            db_product = await db.upsert_product(product_data)

            # Process images for this product
            for image in product.images:
                image_data = {
                    'product_id': db_product['id'],
                    'shopify_image_id': str(image.id),
                    'original_url': image.src,
                    'current_url': image.src,
                    'position': image.position,
                    'width': image.width,
                    'height': image.height
                }
                await db.upsert_image(image_data)

        shopify.ShopifyResource.clear_session()
        return {"status": "success", "message": "Products synced successfully"}

    except Exception as e:
        if 'shopify' in locals():
            shopify.ShopifyResource.clear_session()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle Shopify webhooks."""
    # Verify webhook
    if not verify_shopify_webhook(request):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        # Get webhook data
        webhook_data = await request.json()
        topic = request.headers.get('X-Shopify-Topic')

        # Handle different webhook topics
        if topic == 'products/create':
            # Handle product creation
            pass
        elif topic == 'products/update':
            # Handle product update
            pass
        elif topic == 'products/delete':
            # Handle product deletion
            pass

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 