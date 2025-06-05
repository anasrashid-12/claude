from fastapi import APIRouter

from app.api.v1.endpoints import images, queue, stats

api_router = APIRouter()

api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(queue.router, prefix="/queue", tags=["queue"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"]) 