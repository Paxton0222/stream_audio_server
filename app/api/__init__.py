from app.api.stream import router as stream_router
from app.api.user import router as user_router
from fastapi import APIRouter

api_router = APIRouter(prefix="/api")
api_router.include_router(stream_router)
api_router.include_router(user_router)

__all__ = (
    api_router
)
