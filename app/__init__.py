from passlib.context import CryptContext
from app.models import User
from app.services import WebSocketService, UserService, YoutubeService, RoomService, RedisQueueService, RedisLockService, RedisMapService, RedisPubSubService
from app.repositories import UserRepository
from app.sql import Base, get_db
from app.celery import celery

db = get_db()

# 加密用
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# repositories
user_repository = UserRepository(db)

# 負載平衡 websocket service
socket_service = WebSocketService()
# redis 服務
redis_queue_service = RedisQueueService()
redis_lock_service = RedisLockService()
redis_map_service = RedisMapService()
redis_pub_sub_service = RedisPubSubService()
# 音樂直播房間
room_service = RoomService(lock=redis_lock_service,queue=redis_queue_service,map=redis_map_service)
# Youtube 相關服務
tube_service = YoutubeService()
# 用戶相關服務
user_service = UserService(user_repository, crypt_context)

__all__ = (
    User,
    "socket_service",
    "room_service",
    "tube_service",
    "user_service",
    "redis_queue_service",
    "redis_lock_service",
    "redis_map_service",
    "user_repository",
    "RedisPubSubService",
    "crypt_context",
    "Base",
    "celery"
)
