# app/services/shopify_admin.py
import os
import requests

API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-07")  # update when Shopify bumps

def shopify_graphql(shop_domain: str, access_token: str, query: str, variables: dict=None, timeout: int = 30):
    url = f"https://{shop_domain}/admin/api/{API_VERSION}/graphql.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json={"query": query, "variables": variables or {}}, headers=headers, timeout=timeout)
    if resp.status_code != 200:
        raise Exception(f"Shopify GQL HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        raise Exception(f"Shopify GQL errors: {data['errors']}")
    return data["data"]
