from fastapi import HTTPException, Cookie
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

def get_current_shop(session: str = Cookie(None)) -> str:
    if not session:
        raise HTTPException(status_code=401, detail="Missing session token")
    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise HTTPException(status_code=401, detail="Invalid session payload")
        return shop
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid session")
