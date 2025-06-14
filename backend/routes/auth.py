# backend/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from utils.auth import create_jwt, verify_jwt

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(user_id: str):
    token = create_jwt(user_id)
    return {"access_token": token}

@router.get("/verify")
def verify(token: str):
    return verify_jwt(token)