from fastapi import Request, HTTPException, Cookie, Depends
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")

def get_current_shop(session: str = Cookie(None)) -> str:
    try:
        if not session:
            raise HTTPException(status_code=401, detail="Missing session token")
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        return payload.get("shop")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")
