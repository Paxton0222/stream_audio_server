from fastapi import Depends
from app.models import User
from app.services.socket import WebSocketService
from app.services.redis import get_redis_queue, get_redis_lock, get_redis_map
from app.services.room import RoomService
from app.services.tube import YoutubeService
from app.sql import Base
from app.env import env_vars
from app.celery import celery

socket_service = WebSocketService()
room_service = RoomService(lock=Depends(get_redis_lock),queue=Depends(get_redis_queue),map=Depends(get_redis_map))
tube_service = YoutubeService()

__all__ = (
    User,
    "socket_service",
    "room_service",
    "Base",
    "env_vars",
    "celery"
)
