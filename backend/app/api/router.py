from fastapi import APIRouter
from app.api.endpoints import auth, stores, images, tasks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"]) 