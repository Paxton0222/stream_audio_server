from typing import List
from app.celery import celery
from app.redis import RedisLock, RedisQueue, RedisMap
from app.task import live_stream_youtube_audio
from app.tube import Youtube
import json
import math

class RoomService:
    def __init__(self ,room: str, channel: int, lock: RedisLock, queue: RedisQueue, map: RedisMap):
        self.room = room
        self.channel: channel
        self.lock = lock
        self.queue = queue
        self.map = map
        self.room_name = f"{room}-room-{channel}"
        self.lock_name = f"{room}-lock-{channel}"
        self.map_name = f"{room}-map-{channel}"
    def add(self, url: str) -> None:
        youtube = Youtube()
        info = youtube.audio_info(url)
        if info != None:
            if info["length"] > 3600 * 6:
                return {
                    "status": False,
                    "message": "影片超過6小時上限"
                }
            self.queue.add(self.room_name,info)
            return {
                "status": True
            }
        else:
            return {
                "status": False,
                "message": "無法取得 Youtube 參數"
            }
    def is_playing(self) -> bool:
        task_id = self.get_playing_task_id()
        if task_id != None:
            task = celery.AsyncResult(task_id)
            if task != None:
                if task.state == "PENDING":
                    return True
                elif task.state == "SUCCESS":
                    return True
                elif task.state == "FAILURE":
                    return True
                elif task.state == "REVOKED":
                    return False
        return False
    def set_playing_task_id(self, task_id: str) -> None:
        self.map.set(self.map_name, "playing", task_id)
    def get_playing_task_id(self) -> str:
        return self.map.get(self.map_name, "playing")
    def play(self) -> None:
        if self.queue.length(self.room_name) > 0:
            if self.is_playing():
                return {
                    "status": False,
                    "message": "音樂正在播放中"
                }
            info = json.loads(self.queue.first(self.room_name))
            # 取得被鎖上但是沒有在播放的鎖
            while not self.lock.acquire(self.lock_name, info["length"] + 10):
                self.lock.release(self.lock_name)
            live_stream_youtube_audio.apply_async((info, self.room_name,self.lock_name), retry=False,expire=info["length"] + 10)
            return {
                "status": True
            }
        return {
            "status": False,
            "message": "隊列中沒有音樂可播放"
        }
    def pause(self) -> None:
        if self.is_playing():
            task_id = self.get_playing_task_id()
            task = celery.AsyncResult(task_id)
            task.revoke(terminate=True,signal="SIGTERM")
            return {
                "status": True
            }
        return {
            "status": False
        }
    def list(self, page: int, limit: int) -> List[dict]:
        start_index = (page - 1) * limit
        end_index = start_index + limit - 1
        data = self.queue.range(start_index, end_index)
        length = self.length()
        total_page = math.ceil(length // limit) + 1
        return {
            "total": total_page,
            "data": data
        }
    def length(self) -> int:
        return self.queue.length(self.room_name)
    def clean(self) -> None:
        self.queue.clean(self.room_name)