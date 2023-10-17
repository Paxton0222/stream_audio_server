from fastapi import FastAPI, Depends
from app.task import live_stream_youtube_audio
from app.tube import Youtube
from app.redis import RedisQueue, RedisLock, RedisMap, get_redis_queue, get_redis_lock, get_redis_map
from app.celery import celery
from app.services import RoomService
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stream/add/{room}/{channel}")
def stream_add(room: str, channel: int,url: str, redis_queue: RedisQueue = Depends(get_redis_queue), redis_lock: RedisLock = Depends(get_redis_lock), redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(room,channel,redis_lock,redis_queue,redis_map)
    return room_service.add(url)

@app.get("/stream/play/{room}/{channel}")
def stream_play(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue),redis_map: RedisMap = Depends(get_redis_map)): # 如果當前線程沒有在播放
    room_service = RoomService(room,channel,redis_lock,redis_queue,redis_map)
    return room_service.play()

@app.get("/stream/pause/{room}/{channel}")
def stream_pause(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue),redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(room,channel,redis_lock,redis_queue,redis_map)
    return room_service.pause()

@app.get("/stream/list/{room}/{channel}")
def stream_list(room: str, channel: int, page: int, limit: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue),redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(room,channel,redis_lock,redis_queue,redis_map)
    return room_service.list(page, limit)

@app.get("/stream/list/length/{room}/{channel}")
def stream_length(room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue),redis_map: RedisMap = Depends(get_redis_map)):
    room_service = RoomService(room,channel,redis_lock,redis_queue,redis_map)
    return room_service.length()
