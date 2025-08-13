
# app/services/credits_service.py
from app.services.supabase_service import supabase
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ensure_shop_credits_row(shop_domain: str):
    row = supabase.table("shop_credits").select("*").eq("shop_domain", shop_domain).single().execute().data
    if row is None:
        supabase.table("shop_credits").insert({
            "shop_domain": shop_domain,
            "credits": 0,
            "created_at": now_iso(),
            "updated_at": now_iso()
        }).execute()

def add_credits_and_record(shop: str, credits_to_add: int, plan_id: str, source: str, purchase_id: str):
    """
    Idempotent: if credit_transactions already contains (shop, external_id) we return None.
    Otherwise update shop_credits and insert a credit_transactions row and return new_balance.
    """
    # idempotency check
    existing = supabase.table("credit_transactions") \
        .select("id").eq("shop", shop).eq("external_id", purchase_id).single().execute().data
    if existing:
        return None

    # ensure shop_credits row
    res = supabase.table("shop_credits").select("credits").eq("shop_domain", shop).single().execute()
    if res.data is None:
        new_balance = credits_to_add
        supabase.table("shop_credits").insert({
            "shop_domain": shop,
            "credits": new_balance,
            "created_at": now_iso(),
            "updated_at": now_iso()
        }).execute()
    else:
        current = res.data.get("credits", 0)
        new_balance = current + credits_to_add
        supabase.table("shop_credits").update({
            "credits": new_balance,
            "updated_at": now_iso()
        }).eq("shop_domain", shop).execute()

    # insert transaction
    supabase.table("credit_transactions").insert({
        "shop": shop,
        "change_amount": credits_to_add,
        "reason": f"Purchased {credits_to_add} credits (plan {plan_id})",
        "external_id": purchase_id,
        "source": source,
        "created_at": now_iso()
    }).execute()

    # mark pending if exists (optional)
    supabase.table("credit_pending").update({"status": "COMPLETED", "updated_at": now_iso()}) \
        .eq("shop_domain", shop).eq("purchase_id", purchase_id).execute()

    return new_balance
