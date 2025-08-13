import os, requests

API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-07")
BACKEND_URL = os.getenv("BACKEND_URL")

# Only uninstall webhook uses REST
REST_WEBHOOKS = [
    {"topic": "app/uninstalled", "address": f"{BACKEND_URL}/webhooks/uninstall", "format": "json"}
]

def register_shopify_webhooks(shop: str, access_token: str):
    if not shop.startswith("https://"):
        shop_url = f"https://{shop}"
    else:
        shop_url = shop

    headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}

    # REST webhook registration (optional if you already register uninstall separately)
    for webhook in REST_WEBHOOKS:
        resp = requests.post(f"{shop_url}/admin/api/{API_VERSION}/webhooks.json", json={"webhook": webhook}, headers=headers, timeout=30)
        if resp.status_code not in (201, 422):
            print(f"⚠️ Failed to register REST webhook {webhook['topic']}: {resp.text}")

    # GraphQL registration for one-time purchase webhook
    gql_url = f"{shop_url}/admin/api/{API_VERSION}/graphql.json"
    mutation = """
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        userErrors { field message }
        webhookSubscription { id }
      }
    }
    """
    variables = {
        "topic": "APP_PURCHASES_ONE_TIME_UPDATE",
        "webhookSubscription": {
            "callbackUrl": f"{BACKEND_URL}/webhooks/app_purchases_one_time_update",
            "format": "JSON"
        }
    }
    resp = requests.post(gql_url, json={"query": mutation, "variables": variables}, headers=headers, timeout=30)
    errors = resp.json().get("data", {}).get("webhookSubscriptionCreate", {}).get("userErrors", [])
    if errors:
        print(f"⚠️ GraphQL webhook registration failed: {errors}")
    else:
        print("✅ GraphQL one-time purchase webhook registered")

    return True
