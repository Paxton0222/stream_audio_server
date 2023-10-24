from app.models import User
from app.services import WebSocketService, UserService, YoutubeService, RoomService, get_redis_queue, get_redis_lock, get_redis_map
from app.sql import Base, get_db
from app.celery import celery

socket_service = WebSocketService()
room_service = RoomService(lock=get_redis_lock(),queue=get_redis_queue(),map=get_redis_map())
tube_service = YoutubeService()
user_service = UserService(get_db())

__all__ = (
    User,
    "socket_service",
    "room_service",
    "tube_service",
    "user_service",
    "Base",
    "celery"
)
