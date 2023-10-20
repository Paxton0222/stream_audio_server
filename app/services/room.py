from typing import List
from app.celery import celery
from app.redis import RedisLock, RedisQueue, RedisMap
from app.task import live_stream_youtube_audio
from app.tube import Youtube
import logging
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
        self.room_name = f"{room}-room-{channel}"
        self.lock_name = f"{room}-lock-{channel}"
        self.map_name = f"{room}-map-{channel}"
        self.next_name = f"{room}-next-{channel}"

    def add(self, url: str) -> None:
        youtube = Youtube()
        info = youtube.audio_info(url)
        if info != None:
            if info["length"] > 3600 * 6:
                return {
                    "status": False,
                    "message": "影片超過6小時上限"
                }
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
        task = self.current_task()
        if task != None:
            if task.state == "PENDING":
                return True
            elif task.state == "SUCCESS":
                return True
            elif task.state == "FAILURE":
                return True
            elif task.state == "REVOKED":
                return False
            elif task.state == "STARTED":
                return True
        return False

    def current_task(self) -> str | None:
        self.clear_offline_worker_task()
        task_id = self.get_playing_task_id()
        if task_id != None:
            task = celery.AsyncResult(task_id)
            if task != None:
                return task
        return None

    def clear_offline_worker_task(self):
        control = celery.control
        active_workers = control.inspect().active()
        task_id = self.get_playing_task_id()
        if task_id != None:
            task = celery.AsyncResult(task_id)
            if task.state == "STARTED":
                worker_name = task.info.get("hostname")

                def cancel():
                    logging.info("clear zombie task")
                    celery.control.revoke(
                        task_id.decode('utf-8'), terminate=True)
                    self.cancel_zombie_task_lock()
                if active_workers == None:
                    cancel()
                    return
                if worker_name not in active_workers:
                    cancel()
                else:
                    pass
                    # tasks = active_workers[worker_name]
                    # for t in tasks:
                    #     # 暫時先這樣 O(n)
                    #     logging.info(t['id'], task_id.decode('utf-8'))
                    #     logging.info(t['id'] == task_id.decode('utf-8'))
                    #     if t['id'] == task_id.decode('utf-8'):
                    #         break
                    # else:
                    #     logging.error("task cancel")
                    #     cancel()

    def cancel_zombie_task_lock(self):
        """因為 docker 刪除容器時無法自動解除鎖定狀態，故在操作前檢查"""
        self.map.delete(self.map_name, "playing")
        self.lock.release(self.lock_name)

    def playing_data(self) -> dict:
        data = self.queue.first(self.room_name)
        if data:
            return json.loads(data)
        return {}

    def set_playing_task_id(self, task_id: str) -> None:
        self.map.set(self.map_name, "playing", task_id)

    def get_playing_task_id(self):
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
            task = live_stream_youtube_audio.apply_async(
                (info, self.room, self.channel), retry=False, expire=info["length"] + 10)
            logging.info(task.id)
            self.set_playing_task_id(str(task.id))
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
            task = celery.AsyncResult(task_id.decode('utf-8'))
            if task.state == "PENDING":
                task.revoke(terminate=True)
            else:
                celery.control.revoke(task_id.decode(
                    'utf-8'), terminate=True, signal=signal.SIGTERM)
            self.cancel_zombie_task_lock()
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
        last_time = self.map.get(self.next_name, "last_time")
        if self.is_playing() and (last_time is None or int(time.time()) - int(last_time.decode("utf-8")) > 5):
            pause_res = self.pause()
            if pause_res["status"]:
                self.map.set(self.next_name, "last_time", int(time.time()))
                self.queue.pop(self.room_name)
                return self.play()
            else:
                return {
                    "status": False,
                    "message": "暫停音樂失敗"
                }
        return {
            "status": False,
            "message": "沒有下一首音樂了"
        }

    def list(self, page: int, limit: int) -> List[dict]:
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
        return self.queue.length(self.room_name)

    def clean(self) -> None:
        self.queue.clean(self.room_name)
