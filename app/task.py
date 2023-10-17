from app.celery import celery
from app.exceptions import YoutubeAudioExpired
from app.stream import Stream
from app.redis import get_redis_lock,get_redis_queue, get_redis_map
from app.tube import Youtube
from app.env import env_vars
import json

@celery.task
def live_stream_youtube_audio(info: dict, room_name: str, lock_name: str):
    lock = get_redis_lock()
    queue = get_redis_queue()
    rmap = get_redis_map()
    map_name = f"{room_name}-map-{lock_name}"
    try:
        rmap.set(f"{room_name}-map-{lock_name}", "playing", live_stream_youtube_audio.request.id)
        stream = Stream()
        stream.live_stream_audio(info["audio_url"], f"""{env_vars["RTMP_TARGET"]}/{room_name}""",True)
    except YoutubeAudioExpired:
        print("audio expired.")
        youtube = Youtube()
        updated_info = youtube.audio_info(info["url"])
        if updated_info != None:
            lock.extend(lock_name, updated_info["length"] + 10)
            live_stream_youtube_audio.apply_async((updated_info,room_name,lock_name), retry=False, expire=updated_info["length"] + 10)
        else:
            return None
    finally:
        # 下一首
        queue.pop(room_name)
        next_music = queue.first(room_name)
        if next_music:
            next_music = json.loads(next_music)
            lock.extend(lock_name,next_music["length"] + 10)
            live_stream_youtube_audio.apply_async((next_music,room_name, lock_name), retry=False,expire=next_music["length"] + 10)
        else:
            rmap.delete(map_name, "playing")
            lock.release(lock_name) # 釋放鎖
    return None