# backend/utils/shopify_api.py
import os, requests

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-04")

def get_products(shop_domain):
    url = f"https://{shop_domain}/admin/api/{API_VERSION}/products.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_API_SECRET}
    response = requests.get(url, headers=headers)
    return response.json()