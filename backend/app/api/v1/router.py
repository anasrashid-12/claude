from fastapi import APIRouter
from app.api.v1.endpoints import auth, images, tasks

# Create the main v1 router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"]) 