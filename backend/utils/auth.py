# backend/utils/auth.py
import jwt, os
from fastapi import HTTPException, Header

SECRET = os.getenv("JWT_SECRET", "test")

def create_jwt(user_id: str):
    return jwt.encode({"user_id": user_id}, SECRET, algorithm="HS256")

def verify_jwt(token: str = Header(...)):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")