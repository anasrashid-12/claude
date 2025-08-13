import os, requests

API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-07")

WEBHOOKS_TO_REGISTER = [
    {
        "topic": "app_purchases_one_time/update",
        "address": f"{os.getenv('BACKEND_URL')}/webhooks/app_purchases_one_time_update",
        "format": "json"
    }
]

def register_shopify_webhooks(shop: str, access_token: str):
    """
    Registers required webhooks for a shop. Idempotent: Shopify ignores duplicates.
    """
    # Ensure https prefix
    if not shop.startswith("https://"):
        shop_url = f"https://{shop}"
    else:
        shop_url = shop

    url = f"{shop_url}/admin/api/{API_VERSION}/webhooks.json"
    headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}

    for webhook in WEBHOOKS_TO_REGISTER:
        payload = {"webhook": webhook}
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        # 422 = webhook already exists, ignore
        if resp.status_code not in (201, 422):
            raise Exception(f"Failed to register webhook {webhook['topic']} for {shop}: {resp.text}")
    return True
