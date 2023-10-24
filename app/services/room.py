from app.services.redis import RedisLockService, RedisQueueService, RedisMapService
from app.tasks.stream import live_stream_youtube_audio
from typing import List
from app.celery import celery
import signal
import json
import math
import time

class RoomService:
    def __init__(self, lock: RedisLockService, queue: RedisQueueService, map: RedisMapService):
        self.lock = lock
        self.queue = queue
        self.map = map
    
    def room_name(self, room: str, channel: int):
        """房間名稱"""
        return f"{room}-room-{channel}"
    
    def lock_name(self, room: str, channel: int):
        """房間全局鎖名稱"""
        return f"{room}-lock-{channel}"
    
    def next_name(self, room: str, channel: int):
        """房間全局哈希表名稱"""
        return f"{room}-next-{channel}"
    
    def map_name(self, room: str, channel: int):
        """房間切換下一首全局鎖名稱"""
        return f"{room}-map-{channel}"

    def add(self, info: dict, room: str, channel: int) -> None:
        """加入歌曲到隊列中"""
        if info != None:
            self.queue.add(self.room_name(room,channel), info)
            return {
                "status": True
            }
        else:
            return {
                "status": False,
                "message": "無法取得 Youtube 參數"
            }

    def is_playing(self,room: str, channel: int) -> bool:
        """是否在播放中"""
        task_id = self.get_playing_task_id(room,channel)
        return True if task_id != None else False

    def release_lock(self,room: str, channel: int):
        """解除線程鎖"""
        self.map.delete(self.map_name(room,channel), "playing")
        self.lock.release(self.lock_name(room,channel))

    def playing_data(self, room: str, channel: int) -> dict:
        """播放中的影片資料"""
        data = self.queue.first(self.room_name(room,channel))
        if data:
            return json.loads(data)
        return {}

    def set_playing_task_id(self, task_id: str, room: str, channel: int) -> None:
        """設置正在播放的 task_id"""
        self.map.set(self.map_name(room,channel), "playing", task_id)

    def get_playing_task_id(self, room: str, channel: int):
        """取得正在播放的 task_id"""
        return self.map.get(self.map_name(room,channel), "playing")

    def play(self, room: str, channel: int) -> None:
        """播放隊列歌曲"""
        if self.queue.length(self.room_name(room,channel)) > 0:
            if self.is_playing(room,channel):
                return {
                    "status": False,
                    "message": "音樂正在播放中"
                }
            info = json.loads(self.queue.first(self.room_name(room,channel)))
            # 取得被鎖上但是沒有在播放的鎖
            while not self.lock.acquire(self.lock_name(room,channel), info["length"] + 5):
                self.lock.release(self.lock_name(room,channel))
            task = live_stream_youtube_audio.apply_async(
                (info, room, channel), retry=False, expire=info["length"] + 5)
            self.set_playing_task_id(str(task.id),room,channel)
            return {
                "status": True
            }
        return {
            "status": False,
            "message": "隊列中沒有音樂可播放"
        }

    def pause(self,room: str, channel: int) -> None:
        """暫停播放歌曲"""
        if self.is_playing(room,channel):
            task_id = self.get_playing_task_id(room,channel)
            task = celery.AsyncResult(task_id.decode('utf-8'))
            if task.state == "PENDING":
                task.revoke(terminate=True)
            else:
                celery.control.revoke(task_id.decode(
                    'utf-8'), terminate=True, signal=signal.SIGTERM)
            # self.release_lock()
            return {
                "status": True,
                "state": task.state,
                "task_id": task_id.decode("utf-8")
            }
        return {
            "status": False,
            "message": "音樂正在播放中"
        }

    def next(self, room: str, channel: int):
        """切換下一首歌"""
        last_time = self.map.get(self.next_name(room,channel), "last_time")
        if (last_time is None or int(time.time()) - int(last_time.decode("utf-8")) > 5):
            self.map.set(self.next_name(room,channel), "last_time", int(time.time()))
            if self.is_playing(room,channel):
                self.pause(room,channel)
                while self.is_playing(room,channel):
                    time.sleep(0.1)
                self.queue.pop(self.room_name(room,channel))
                return self.play(room,channel)
            else:
                if self.queue.length(self.room_name(room,channel)) > 0:
                    self.queue.pop(self.room_name(room,channel))
                    return self.play(room,channel)
                return {
                    "status": False,
                    "message": "沒有下一首音樂了"
                }
        else:
            return {
                "stauts": False,
                "message": "操作過快"
            }

    def list(self, page: int, limit: int, room: str, channel: int) -> List[dict]:
        """取得隊列列表"""
        start_index = (page - 1) * limit
        end_index = start_index + limit - 1
        data = self.queue.range(self.room_name(room,channel), start_index, end_index)
        length = self.length(room,channel)
        total_page = math.ceil(length // limit) + 1
        return {
            "total": total_page,
            "length": length,
            "data": data
        }

    def length(self,room: str, channel: int) -> int:
        """取得隊列長度"""
        return self.queue.length(self.room_name(room,channel))

    def clean(self, room: str, channel: int) -> None:
        """清除隊列"""
        self.queue.clean(self.room_name(room,channel))
