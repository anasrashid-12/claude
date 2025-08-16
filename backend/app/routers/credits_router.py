# routers/credits_router.py
from fastapi import APIRouter, Request, HTTPException, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from app.services.supabase_service import supabase
from app.services.shopify_admin import shopify_graphql
from app.services.credits_service import add_credits_and_record, now_iso
from app.config.plans import PLANS
import os, jwt, time

credits_router = APIRouter(prefix="")

# ────────────────── Environment & Config ──────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")
APP_URL = os.getenv("BACKEND_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")
CURRENCY = os.getenv("CREDITS_CURRENCY", "USD")
SANDBOX_MODE = os.getenv("SANDBOX_MODE", "true").lower() == "true"

if not APP_URL or not FRONTEND_URL:
    raise RuntimeError("BACKEND_URL and FRONTEND_URL must be set")

# ────────────────── Session & Shop ──────────────────
def get_shop_from_session(session: str):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")
    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise HTTPException(status_code=400, detail="Invalid session")
        return shop
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session")

def get_access_token(shop: str) -> str:
    res = supabase.table("shops").select("access_token").eq("shop", shop).maybe_single().execute()
    shop_data = getattr(res, "data", None)
    if not shop_data or not shop_data.get("access_token"):
        raise HTTPException(status_code=401, detail="Missing Shopify access token")
    return shop_data["access_token"]

# ────────────────── Create Checkout ──────────────────
@credits_router.post("/credits/checkout")
async def create_checkout(request: Request, session: str = Cookie(None)):
    shop = get_shop_from_session(session)
    body = await request.json()
    plan_id = str(body.get("planId"))
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    plan = PLANS[plan_id]

    if SANDBOX_MODE:
        purchase_id = f"sandbox_{shop}_{plan_id}_{int(time.time())}"
        confirmation_url = f"{APP_URL}/credits/confirm?planId={plan_id}&sandbox=true&purchaseId={purchase_id}"

        # Insert pending record
        supabase.table("credit_pending").insert({
            "shop_domain": shop,
            "plan_id": plan_id,
            "purchase_id": purchase_id,
            "name": f"Maxflow Credits {plan['credits']}",
            "status": "PENDING",
            "created_at": now_iso()
        }).execute()

        return JSONResponse({"confirmationUrl": confirmation_url})

    # Real Shopify billing
    access_token = get_access_token(shop)
    return_url = f"{APP_URL}/credits/confirm?planId={plan_id}"

    mutation = """
    mutation AppPurchaseOneTimeCreate($name: String!, $price: MoneyInput!, $returnUrl: URL!) {
      appPurchaseOneTimeCreate(name: $name, price: $price, returnUrl: $returnUrl) {
        userErrors { field message }
        appPurchaseOneTime { id createdAt }
        confirmationUrl
      }
    }
    """
    name = f"Maxflow Credits {plan['credits']}"
    variables = {
        "name": name,
        "price": {"amount": plan["price"], "currencyCode": CURRENCY},
        "returnUrl": return_url
    }

    data = shopify_graphql(shop, access_token, mutation, variables)
    payload = data.get("appPurchaseOneTimeCreate", {})
    if payload.get("userErrors"):
        raise HTTPException(status_code=400, detail=str(payload["userErrors"]))

    purchase_id = payload.get("appPurchaseOneTime", {}).get("id")
    confirmation_url = payload.get("confirmationUrl")
    if not confirmation_url:
        raise HTTPException(status_code=500, detail="Failed to generate Shopify confirmation URL")

    # Insert pending record
    supabase.table("credit_pending").insert({
        "shop_domain": shop,
        "plan_id": plan_id,
        "purchase_id": purchase_id,
        "name": name,
        "status": "PENDING",
        "created_at": now_iso()
    }).execute()

    return JSONResponse({"confirmationUrl": confirmation_url})

# ────────────────── Confirm Purchase ──────────────────
@credits_router.get("/credits/confirm")
async def confirm_after_return(planId: str, session: str = Cookie(None), sandbox: str = None, purchaseId: str = None):
    shop = get_shop_from_session(session)
    plan_id = str(planId)
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid planId")

    plan = PLANS[plan_id]

    if SANDBOX_MODE or sandbox:
        if not purchaseId:
            raise HTTPException(status_code=400, detail="Missing sandbox purchaseId")
        new_balance = add_credits_and_record(shop, plan["credits"], plan_id, "sandbox", purchaseId)
        print(f"[sandbox] {shop} credits updated: {new_balance}")
        return RedirectResponse(f"{FRONTEND_URL}/dashboard?credits_added={plan['credits']}")

    # Real Shopify billing verification
    access_token = get_access_token(shop)
    query = """
    query {
      currentAppInstallation {
        oneTimePurchases(first: 20) {
          edges { node { id name status adminGraphqlApiId createdAt } }
        }
      }
    }
    """
    data = shopify_graphql(shop, access_token, query)
    purchases = [edge["node"] for edge in data.get("currentAppInstallation", {}).get("oneTimePurchases", {}).get("edges", [])]

    target_name = f"Maxflow Credits {plan['credits']}"
    active = next((p for p in purchases if p["name"] == target_name and p["status"] == "ACTIVE"), None)

    if not active:
        return RedirectResponse(f"{FRONTEND_URL}/payment-pending")

    add_credits_and_record(
        shop,
        plan["credits"],
        plan_id,
        "callback",
        active.get("adminGraphqlApiId") or active.get("id")
    )

    return RedirectResponse(f"{FRONTEND_URL}/dashboard?credits_added={plan['credits']}")

@credits_router.get("/credits/me")
async def get_my_credits(session: str = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    shop = get_shop_from_session(session)
    if not shop:
        raise HTTPException(status_code=401, detail="Invalid session")

    resp = supabase.table("shop_credits").select("credits").eq("shop", shop).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Shop not found")

    return {"credits": resp.data["credits"]}