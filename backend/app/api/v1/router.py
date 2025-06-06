from fastapi import APIRouter
from app.api.v1.endpoints import auth, stores, images, tasks

# Create the main v1 router
router = APIRouter(prefix="/v1")

# Include all route modules
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(stores.router, prefix="/stores", tags=["Stores"])
router.include_router(images.router, prefix="/images", tags=["Images"])
router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"]) 