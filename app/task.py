from app.celery import celery
from app.exceptions import YoutubeAudioExpired
from app.stream import Stream
from app.redis import get_redis_lock,get_redis_queue, get_redis_map
from app.tube import Youtube
from app.env import env_vars
import json

@celery.task
def live_stream_youtube_audio(info: dict, room: str, channel:int):
    lock = get_redis_lock()
    queue = get_redis_queue()
    rmap = get_redis_map()
    room_name = f"{room}-room-{channel}"
    lock_name = f"{room}-lock-{channel}"
    map_name = f"{room}-map-{channel}"
    stream = Stream()
    try:
        stream.live_stream_audio(info["audio_url"], f"""{env_vars["RTMP_TARGET"]}/{room_name}""",True)
    except YoutubeAudioExpired:
        youtube = Youtube()
        updated_info = youtube.audio_info(info["url"])
        if updated_info != None:
            lock.extend(lock_name, updated_info["length"] + 10)
            task = live_stream_youtube_audio.apply_async((updated_info,room,channel), retry=False, expire=updated_info["length"] + 10)
            rmap.set(map_name, "playing", str(task.id))
        else:
            return None
    except Exception as e:
        print("error",e)
    finally:
        # 下一首
        if celery.AsyncResult(live_stream_youtube_audio.request.id).state != "REVOKED":
            queue.pop(room_name)
            next_music = queue.first(room_name)
            if next_music:
                next_music = json.loads(next_music)
                lock.extend(lock_name,next_music["length"] + 10)
                task = live_stream_youtube_audio.apply_async((next_music,room, channel), retry=False,expire=next_music["length"] + 10)
                rmap.set(map_name, "playing", str(task.id))
            else:
                rmap.delete(map_name, "playing")
                lock.release(lock_name) # 釋放鎖 
        else:
            rmap.delete(map_name, "playing")
            lock.release(lock_name) # 釋放鎖 
    return None
