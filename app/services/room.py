from app.redis import RedisLock, RedisQueue, RedisMap
from app.services.tube import YoutubeService
from app.tasks.stream import live_stream_youtube_audio
from typing import List
from app.celery import celery
import signal
import json
import math
import time


class RoomService:
    def __init__(self, room: str, channel: int, lock: RedisLock, queue: RedisQueue, map: RedisMap):
        self.room = room
        self.channel = channel
        self.lock = lock
        self.queue = queue
        self.map = map
        self.room_name = f"{room}-room-{channel}"  # 房間名稱
        self.lock_name = f"{room}-lock-{channel}"  # 房間全局鎖名稱
        self.map_name = f"{room}-map-{channel}"  # 房間全局哈希表名稱
        self.next_name = f"{room}-next-{channel}"  # 房間切換下一首全局鎖名稱

    def add(self, url: str) -> None:
        """加入歌曲到隊列中"""
        youtube = YoutubeService()
        info = youtube.info(url)
        if info != None:
            #     if info["length"] > 3600 * 6:
            #         return {
            #             "status": False,
            #             "message": "影片超過6小時上限"
            #         }
            self.queue.add(self.room_name, info)
            return {
                "status": True
            }
        else:
            return {
                "status": False,
                "message": "無法取得 Youtube 參數"
            }

    def is_playing(self) -> bool:
        """是否在播放中"""
        task_id = self.get_playing_task_id()
        return True if task_id != None else False

    def release_lock(self):
        """解除線程鎖"""
        self.map.delete(self.map_name, "playing")
        self.lock.release(self.lock_name)

    def playing_data(self) -> dict:
        """播放中的影片資料"""
        data = self.queue.first(self.room_name)
        if data:
            return json.loads(data)
        return {}

    def set_playing_task_id(self, task_id: str) -> None:
        """設置正在播放的 task_id"""
        self.map.set(self.map_name, "playing", task_id)

    def get_playing_task_id(self):
        """取得正在播放的 task_id"""
        return self.map.get(self.map_name, "playing")

    def play(self) -> None:
        """播放隊列歌曲"""
        if self.queue.length(self.room_name) > 0:
            if self.is_playing():
                return {
                    "status": False,
                    "message": "音樂正在播放中"
                }
            info = json.loads(self.queue.first(self.room_name))
            # 取得被鎖上但是沒有在播放的鎖
            while not self.lock.acquire(self.lock_name, info["length"] + 5):
                self.lock.release(self.lock_name)
            task = live_stream_youtube_audio.apply_async(
                (info, self.room, self.channel), retry=False, expire=info["length"] + 5)
            self.set_playing_task_id(str(task.id))
            return {
                "status": True
            }
        return {
            "status": False,
            "message": "隊列中沒有音樂可播放"
        }

    def pause(self) -> None:
        """暫停播放歌曲"""
        if self.is_playing():
            task_id = self.get_playing_task_id()
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

    def next(self):
        """切換下一首歌"""
        last_time = self.map.get(self.next_name, "last_time")
        if (last_time is None or int(time.time()) - int(last_time.decode("utf-8")) > 5):
            self.map.set(self.next_name, "last_time", int(time.time()))
            if self.is_playing():
                self.pause()
                while self.is_playing():
                    time.sleep(0.1)
                self.queue.pop(self.room_name)
                return self.play()
            else:
                if self.queue.length(self.room_name) > 0:
                    self.queue.pop(self.room_name)
                    return self.play()
                return {
                    "status": False,
                    "message": "沒有下一首音樂了"
                }
        else:
            return {
                "stauts": False,
                "message": "操作過快"
            }

    def list(self, page: int, limit: int) -> List[dict]:
        """取得隊列列表"""
        start_index = (page - 1) * limit
        end_index = start_index + limit - 1
        data = self.queue.range(self.room_name, start_index, end_index)
        length = self.length()
        total_page = math.ceil(length // limit) + 1
        return {
            "total": total_page,
            "length": length,
            "data": data
        }

    def length(self) -> int:
        """取得隊列長度"""
        return self.queue.length(self.room_name)

    def clean(self) -> None:
        """清除隊列"""
        self.queue.clean(self.room_name)
