# backend/routers/me_router.py
from fastapi import APIRouter, Request, HTTPException, Cookie
import jwt
import os

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

@router.get("/me")
async def get_shop_info(session: str = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session token")
    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        return {"shop": payload["shop"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid session token")
