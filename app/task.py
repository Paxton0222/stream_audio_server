from app.celery import celery
from app.exceptions import YoutubeAudioExpired
from app.stream import Stream
from app.redis import get_redis_lock, get_redis_queue, get_redis_map
from app.tube import Youtube
from app.env import env_vars
import json
import signal
import logging
import os

@celery.task
def live_stream_youtube_audio(info: dict, room: str, channel: int):
    lock = get_redis_lock()
    queue = get_redis_queue()
    rmap = get_redis_map()
    room_name = f"{room}-room-{channel}"
    lock_name = f"{room}-lock-{channel}"
    map_name = f"{room}-map-{channel}"
    stream = Stream()
    process = None  # 初始化 process 变量

    def release_lock(signum = None, frame = None):
        rmap.delete(map_name, "playing")
        lock.release(lock_name)  # 释放锁
        logging.info(f"{room_name} released lock successfully.")

    def terminate_process(signum, frame):
        nonlocal process
        if process:
            logging.info(f"{room_name} terminating process...")
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                logging.info(f"{room_name} terminated process successfully.")
            except ProcessLookupError:
                # 处理已经终止的 process
                logging.error(f"{room_name} Failed to terminate process.")
        release_lock()
    
    def next_music():
        # 下一首
        if celery.AsyncResult(live_stream_youtube_audio.request.id).state != "REVOKED":
            queue.pop(room_name)
            logging.info(f"Room {room_name} music poped: {info['title']}")
            next_music = queue.first(room_name)
            if next_music:
                next_music = json.loads(next_music)
                lock.extend(lock_name, next_music["length"] + 10)
                task = live_stream_youtube_audio.apply_async((next_music, room, channel), retry=False, expire=next_music["length"] + 10)
                rmap.set(map_name, "playing", str(task.id))
                return None
            else:
                release_lock()

    # 设置 SIGTERM 信号处理程序
    signal.signal(signal.SIGTERM, terminate_process)

    try:
        logging.info(f"Room {room_name} playing music: {info['title']}")
        process = stream.live_stream_audio(info["audio_url"], f"""{env_vars["RTMP_TARGET"]}/{room_name}""", False)
        process.wait()
        logging.info(f"Room {room_name} music ended: {info['title']}")
        next_music()
        logging.info("{room_name} end of script")
    except YoutubeAudioExpired:
        logging.info(f"{room_name} {info['title']} audio url is expired restarting task...")
        youtube = Youtube()
        updated_info = youtube.audio_info(info["url"])
        if updated_info:
            lock.extend(lock_name, updated_info["length"] + 10)
            task = live_stream_youtube_audio.apply_async((updated_info, room, channel), retry=False, expire=updated_info["length"] + 10)
            rmap.set(map_name, "playing", str(task.id))
        else:
            logging.error("Couldn't find music info.")
            next_music()
    except Exception as e:
        logging.error(e)
