from fastapi import APIRouter
from app import user_service

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/{id}")
async def get_user_by_id(id: int):
    return user_service.get_user_by_id(id)
