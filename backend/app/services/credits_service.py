# app/services/credits_service.py
from app.services.supabase_service import supabase
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ensure_shop_credits_row(shop_domain: str):
    res = supabase.table("shop_credits").select("*").eq("shop_domain", shop_domain).maybe_single().execute()
    row = getattr(res, "data", None)
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
    res = supabase.table("credit_transactions") \
        .select("id").eq("shop", shop).eq("external_id", purchase_id).maybe_single().execute()
    existing = getattr(res, "data", None)
    if existing:
        return None

    # ensure shop_credits row
    res = supabase.table("shop_credits").select("credits").eq("shop_domain", shop).maybe_single().execute()
    current_credits = getattr(res, "data", {}).get("credits", 0) if res else 0

    new_balance = current_credits + credits_to_add

    if not getattr(res, "data", None):
        # insert new row
        supabase.table("shop_credits").insert({
            "shop_domain": shop,
            "credits": new_balance,
            "created_at": now_iso(),
            "updated_at": now_iso()
        }).execute()
    else:
        # update existing
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

    # mark pending if exists
    supabase.table("credit_pending").update({"status": "COMPLETED", "updated_at": now_iso()}) \
        .eq("shop_domain", shop).eq("purchase_id", purchase_id).execute()

    return new_balance
