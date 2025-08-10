# routers/credits_router.py
from fastapi import APIRouter, Request, HTTPException, Cookie
from app.services.supabase_service import supabase
import os
import jwt
from datetime import datetime

credits_router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

# Ye plans frontend ke sath match karne chahiye
PLANS = {
    "100": {"credits": 100, "price": 10},
    "500": {"credits": 500, "price": 45},
    "1000": {"credits": 1000, "price": 75},
    "5000": {"credits": 5000, "price": 300},
}

@credits_router.post("/credits/buy")
async def buy_credits(request: Request, session: str = Cookie(None)):
    """
    Simple test version:
    1. Validate shop from cookie
    2. Find plan and add credits
    3. Save in shop_credits and credit_transactions
    """
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise HTTPException(status_code=400, detail="Invalid session")

        body = await request.json()
        plan_id = body.get("planId")
        if plan_id not in PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan ID")

        plan = PLANS[plan_id]
        credits_to_add = plan["credits"]

        # 1. Get or create shop_credits row
        res = supabase.table("shop_credits").select("*").eq("shop_domain", shop).single().execute()
        if res.data is None:
            # Create new row
            supabase.table("shop_credits").insert({
                "shop_domain": shop,
                "credits": credits_to_add,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            new_balance = credits_to_add
        else:
            # Update existing row
            current_credits = res.data.get("credits", 0)
            new_balance = current_credits + credits_to_add
            supabase.table("shop_credits").update({
                "credits": new_balance,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("shop_domain", shop).execute()

        # 2. Insert transaction record
        supabase.table("credit_transactions").insert({
            "shop": shop,
            "change_amount": credits_to_add,
            "reason": f"Purchased {credits_to_add} credits (plan {plan_id})",
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return {"success": True, "new_balance": new_balance}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
