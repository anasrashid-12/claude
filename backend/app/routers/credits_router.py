# routers/credits_router.py
from fastapi import APIRouter, Request, HTTPException, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from app.services.supabase_service import supabase
from app.services.shopify_admin import shopify_graphql
from app.services.credits_service import ensure_shop_credits_row, add_credits_and_record, now_iso
from app.config.plans import PLANS
import os, jwt

router = APIRouter(prefix="")

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")
APP_URL = os.getenv("BACKEND_URL")      # your public backend URL e.g. https://api.example.com
FRONTEND_URL = os.getenv("FRONTEND_URL")  # frontend to redirect merchant after successful payment
CURRENCY = os.getenv("CREDITS_CURRENCY", "USD")

if not APP_URL:
    raise RuntimeError("BACKEND_URL env var must be set")
if not FRONTEND_URL:
    raise RuntimeError("FRONTEND_URL env var must be set")

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

def get_access_token(shop_domain: str) -> str:
    res = supabase.table("shops").select("access_token").eq("shop_domain", shop_domain).single().execute()
    if not res.data or not res.data.get("access_token"):
        raise HTTPException(status_code=401, detail="Missing Shopify access token")
    return res.data["access_token"]

@router.post("/credits/checkout")
async def create_checkout(request: Request, session: str = Cookie(None)):
    """
    Create Shopify one-time app purchase and return confirmationUrl.
    Frontend should redirect merchant to confirmationUrl (top window).
    """
    shop = get_shop_from_session(session)
    body = await request.json()
    plan_id = str(body.get("planId"))
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    plan = PLANS[plan_id]
    access_token = get_access_token(shop)

    # returnUrl must include planId so we can match on return
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
    payload = data["appPurchaseOneTimeCreate"]
    if payload.get("userErrors"):
        raise HTTPException(status_code=400, detail=str(payload["userErrors"]))

    purchase_id = payload["appPurchaseOneTime"]["id"]
    confirmation_url = payload["confirmationUrl"]

    # record pending row to help later verification
    supabase.table("credit_pending").insert({
        "shop_domain": shop,
        "plan_id": plan_id,
        "purchase_id": purchase_id,
        "name": name,
        "status": "PENDING",
        "created_at": now_iso()
    }).execute()

    return JSONResponse({"confirmationUrl": confirmation_url})

@router.get("/credits/confirm")
async def confirm_after_return(planId: str, session: str = Cookie(None)):
    """
    Called when merchant returns from Shopify after approving (or declining) the purchase.
    We check for ACTIVE purchase; if active we credit and redirect to dashboard.
    """
    shop = get_shop_from_session(session)
    plan_id = str(planId)
    if plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid planId")

    plan = PLANS[plan_id]
    access_token = get_access_token(shop)

    query = """
    query {
      currentAppInstallation {
        oneTimePurchases(first: 20) {
          edges {
            node { id name status adminGraphqlApiId createdAt }
          }
        }
      }
    }
    """
    data = shopify_graphql(shop, access_token, query)
    purchases = [edge["node"] for edge in data["currentAppInstallation"]["oneTimePurchases"]["edges"]]

    target_name = f"Maxflow Credits {plan['credits']}"
    active = next((p for p in purchases if p["name"] == target_name and p["status"] == "ACTIVE"), None)

    if not active:
        # Not active yet → send merchant to a friendly pending page on frontend
        return RedirectResponse(url=f"{FRONTEND_URL}/payment-pending")

    # Idempotent credit add
    new_balance = add_credits_and_record(
        shop=shop,
        credits_to_add=plan["credits"],
        plan_id=plan_id,
        source="callback",
        purchase_id=active.get("adminGraphqlApiId") or active.get("id")
    )

    # If new_balance is None then already processed; still redirect to dashboard
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?credits_added={plan['credits']}")
