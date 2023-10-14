from fastapi import FastAPI, Depends
from app.task import live_stream_youtube_audio
from app.tube import Youtube
from app.redis import RedisQueue, RedisLock, get_redis_queue, get_redis_lock, redis_conn
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stream/{room}/{channel}")
def stream(room: str, channel: int,url: str, redis_queue: RedisQueue = Depends(get_redis_queue), redis_lock: RedisLock = Depends(get_redis_lock)):
    youtube = Youtube()
    info = youtube.audio_info(url)
    room_name = f"{room}-room-{channel}"
    lock_name = f"{room}-lock-{channel}"
    if info != None:
        if redis_lock.acquire(lock_name):
            task = live_stream_youtube_audio.apply_async((info["audio_url"],room_name, lock_name), retry=False)
            return {
                "status": True,
                "task_id": task.id
            }
        else:
            redis_queue.add(room_name, info)
            return  {"status": True, "message": f"已經加入等待隊列中"}
    else:
        return {
            "status": False,
            "message": "無法取得 Youtube 參數"
        }

@app.get("/stream/list/{room}/{channel}")
def stream_list(room: str, channel: int, redis_queue: RedisQueue = Depends(get_redis_queue)):
    return redis_queue.range(f"{room}-room-{channel}",0,-1)
