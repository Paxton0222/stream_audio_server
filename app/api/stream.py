from fastapi import Depends,APIRouter
from app.redis import RedisQueue, RedisLock, RedisMap, get_redis_queue, get_redis_lock, get_redis_map
from app.services import RoomService

router = APIRouter(prefix="/stream",tags=["stream"])

@router.post("/add/{room}/{channel}")
async def stream_add(room: str, channel: int, url: str, redis_queue: RedisQueue = Depends(get_redis_queue), redis_lock: RedisLock = Depends(get_redis_lock), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    return room_service.add(url)

@router.post("/play/{room}/{channel}")
async def stream_play(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):  # 如果當前線程沒有在播放
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    return room_service.play()


@router.post("/pause/{room}/{channel}")
async def stream_pause(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    return room_service.pause()


@router.get("/state/{room}/{channel}")
async def stream_state(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    state = room_service.is_playing()
    task = room_service.current_task()
    return {
        "status": state,
        "state": task.state if task != None else None,
        "task_id": room_service.get_playing_task_id(),
        "data": room_service.playing_data() if state else {}
    }


@router.post("/next/{room}/{channel}")
async def stream_next(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    return room_service.next()


@router.get("/list/{room}/{channel}")
async def stream_list(room: str, channel: int, page: int, limit: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    return room_service.list(page, limit)


@router.get("/list/length/{room}/{channel}")
async def stream_length(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(
        room, channel, redis_lock, redis_queue, redis_map)
    return room_service.length()
