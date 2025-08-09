import os
import logging
from supabase import create_client
from datetime import datetime

logger = logging.getLogger("supabase_service")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def save_shop_token(shop: str, access_token: str):
    try:
        logger.info(f"[Supabase] 🔄 Upserting token for {shop}")
        response = supabase.table("shops").upsert(
            {"shop": shop, "access_token": access_token},
            on_conflict="shop"
        ).execute()
        logger.info(f"[Supabase] ✅ Token saved for {shop}")
        return response.data
    except Exception as e:
        logger.exception(f"[Supabase] ❌ Failed to save token for {shop}: {e}")
        raise

# 🆕 Credit-related helpers
def initialize_shop_credits(shop_domain: str, initial_credits: int = 10):
    """Set up credits for a new shop if not already exists."""
    existing = supabase.table("shop_credits").select("*").eq("shop_domain", shop_domain).execute()
    if existing.data:
        return existing.data[0]
    return supabase.table("shop_credits").insert({
        "shop_domain": shop_domain,
        "credits": initial_credits
    }).execute().data

def get_shop_credits(shop_domain: str) -> int:
    res = supabase.table("shop_credits").select("credits").eq("shop_domain", shop_domain).execute()
    if not res.data:
        raise ValueError("Shop credits not found")
    return res.data[0]["credits"]

def deduct_shop_credit(shop_domain: str, amount: int = 1):
    current = get_shop_credits(shop_domain)
    if current < amount:
        raise ValueError("Not enough credits")
    new_balance = current - amount
    supabase.table("shop_credits").update({"credits": new_balance}).eq("shop_domain", shop_domain).execute()
    log_credit_transaction(shop_domain, -amount, "Image processing")
    return new_balance

def add_shop_credits(shop_domain: str, amount: int, reason: str):
    current = get_shop_credits(shop_domain)
    new_balance = current + amount
    supabase.table("shop_credits").update({"credits": new_balance}).eq("shop_domain", shop_domain).execute()
    log_credit_transaction(shop_domain, amount, reason)
    return new_balance

def log_credit_transaction(shop_domain: str, change_amount: int, reason: str):
    supabase.table("credit_transactions").insert({
        "shop": shop_domain,
        "change_amount": change_amount,
        "reason": reason,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
