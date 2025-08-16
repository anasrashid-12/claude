# routers/shopify_webhooks.py
from fastapi import APIRouter, Request, Header, HTTPException
import os, hmac, hashlib, base64, json, logging
from app.services.credits_service import ensure_shop_credits_row, add_credits_and_record, now_iso
from app.services.supabase_service import supabase
from app.config.plans import PLANS

router = APIRouter(prefix="")

logger = logging.getLogger("webhooks")

APP_SECRET = os.getenv("SHOPIFY_API_SECRET")  # must be set

def verify_hmac(raw_body: bytes, hmac_header: str):
    digest = hmac.new(APP_SECRET.encode("utf-8"), raw_body, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode()
    return hmac.compare_digest(computed, (hmac_header or ""))

@router.post("/webhooks/app_purchases_one_time_update")
async def one_time_update(request: Request, x_shopify_hmac_sha256: str = Header(None), x_shopify_shop_domain: str = Header(None)):
    raw = await request.body()
    if not verify_hmac(raw, x_shopify_hmac_sha256):
        logger.warning("Invalid HMAC for webhook")
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    payload = json.loads(raw.decode())
    purchase = payload.get("app_purchase_one_time") or payload.get("appPurchaseOneTime") or {}
    status = purchase.get("status")
    purchase_id = purchase.get("admin_graphql_api_id") or purchase.get("id")
    name = purchase.get("name", "")

    if status != "ACTIVE":
        return {"ok": True}

    # infer plan by name "Maxflow Credits {credits}"
    credits_part = None
    if "Maxflow Credits" in name:
        parts = name.rsplit(" ", 1)
        if len(parts) == 2:
            credits_part = parts[1]

    plan_key = None
    for pid, info in PLANS.items():
        if str(info["credits"]) == str(credits_part):
            plan_key = pid
            break

    if not plan_key:
        logger.info("Webhook purchase name did not match any plan, ignoring.")
        return {"ok": True}

    # idempotent credit add
    ensure_shop_credits_row(x_shopify_shop_domain)
    add_credits_and_record(
        shop=x_shopify_shop_domain,
        credits_to_add=PLANS[plan_key]["credits"],
        plan_id=plan_key,
        source="webhook",
        purchase_id=purchase_id
    )

    # update credit_pending if any
    supabase.table("credit_pending").update({"status": "ACTIVE", "updated_at": now_iso()}) \
        .eq("shop_domain", x_shopify_shop_domain).eq("purchase_id", purchase_id).execute()

    return {"ok": True}
