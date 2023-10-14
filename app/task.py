from app.celery import celery
from app.stream import Stream
from app.redis import get_redis_lock,get_redis_queue
import json

@celery.task
def live_stream_youtube_audio(audio_url: str, room_name: str, lock_name: str):
    try:
        stream = Stream()
        stream.live_stream_audio(audio_url, f"rtmp://localhost:1935/live/{room_name}",True)
    except Exception as e:
        pass
    finally:
        def callback():
            lock = get_redis_lock()
            queue = get_redis_queue()
            next_music = queue.pop(room_name)
            if next_music:
                next_music = json.loads(next_music)
                live_stream_youtube_audio.apply_async((next_music["audio_url"],room_name, lock_name), retry=False)
            else:
                lock.release(lock_name) # 釋放鎖
        callback()
        # live_stream_youtube_audio.request.callbacks.append(callback)