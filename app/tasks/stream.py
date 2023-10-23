from celery.signals import worker_shutting_down, task_success
from app.services.stream import StreamService
from app.services.redis import get_redis_lock, get_redis_map, redis_conn
from app.env import env_vars
from app.celery import celery
import logging
import asyncio
import websockets
import requests
import socket
import signal
import json
import os

worker_hostname = socket.gethostname()
active_radios_key = f'active_radios'


@celery.task
def live_stream_youtube_audio(info: dict, room: str, channel: int):
    lock = get_redis_lock()  # redis lock
    rmap = get_redis_map()  # redis hash map
    room_name = f"{room}-room-{channel}"  # 房間名稱
    lock_name = f"{room}-lock-{channel}"  # 房間全局鎖名稱
    map_name = f"{room}-map-{channel}"  # 房間全局哈希名稱
    stream = StreamService()
    process = None  # Youtube live stream subprocess

    async def send_websocket_event(event: str):
        """
        發送 websocket notification 提醒前端
        """
        uri = f"""{env_vars["WEBSOCKET_URL"]}/api/stream/{room}/{channel}"""
        try:
            async with websockets.connect(uri) as websocket:
                logging.info("Connected to WebSocket server.")
                message = {
                    "type": "worker",
                    "message": event
                }
                await websocket.send(json.dumps(message))
                logging.info("message sent.")
        except Exception as e:
            logging.error(e)

    # 發送 play 通知
    asyncio.get_event_loop().run_until_complete(send_websocket_event("play"))

    def release_lock(signum=None, frame=None):
        """解鎖房間線程"""
        rmap.delete(map_name, "playing")
        lock.release(lock_name)
        logging.info(f"{room_name} released lock successfully.")

    def terminate_process(signum, frame):
        """接收到 celery revoke 訊號時關閉 Youtube subprocess"""
        nonlocal process
        if process:
            logging.info(f"{room_name} terminating process...")
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                logging.info(f"{room_name} terminated process successfully.")
            except ProcessLookupError:
                logging.error(f"{room_name} Failed to terminate process.")

        # 去除掉 task 執行紀錄 (revoke)
        active_radios = json.loads(redis_conn.hget(
            active_radios_key, worker_hostname) or '{}')
        if room_name in active_radios:
            del active_radios[room_name]
        redis_conn.hset(active_radios_key, worker_hostname,
                        json.dumps(active_radios))

    # 設置 revoke callback
    signal.signal(signal.SIGTERM, terminate_process)

    logging.info(f"Room {room_name} playing music: {info['title']}")

    # 增加 task 執行紀錄到 redis (以便 Container down 時可以解鎖)
    active_radios = json.loads(redis_conn.hget(
        active_radios_key, worker_hostname) or '{}')
    active_radios[room_name] = {
        "room": room,
        "channel": channel
    }
    redis_conn.hset(active_radios_key, worker_hostname,
                    json.dumps(active_radios))

    try:
        # 開始 yt 推流 subprocess
        process = stream.live_stream_audio(
            info["url"], f"""{env_vars["RTMP_TARGET"]}/{room_name}""", True)
        process.wait()
        logging.info(f"Room {room_name} music ended: {info['title']}")
    except Exception as e:
        logging.info(e)
    finally:
        # 不管有沒有執行完畢 解鎖
        release_lock()
        # 發送 websocket 停止通知
        asyncio.get_event_loop().run_until_complete(
            send_websocket_event("pause"))

    # 檢查是否 revoke 和 解除 active 狀態
    active_radios = json.loads(redis_conn.hget(
        active_radios_key, worker_hostname) or '{}')
    if room_name in active_radios:
        del active_radios[room_name]
        redis_conn.hset(active_radios_key, worker_hostname,
                        json.dumps(active_radios))
    else:
        raise Exception("revoke")

    logging.info(f"{room_name} end of script")

    return {
        "room": room,
        "channel": channel
    }


@task_success.connect(sender=live_stream_youtube_audio)
def live_stream_youtube_audio_success(sender, result, **kargs):
    """
    下一首 callback
    """
    room = result["room"]
    channel = result["channel"]
    live_stream_next_youtube_audio.apply_async(
        args=(room, channel), retry=False, expire=5)


@celery.task
def live_stream_next_youtube_audio(room: str, channel: int):
    """
    下一首
    """
    res = requests.post(
        f"""{env_vars["BACKEND_URL"]}/api/stream/next/{room}/{channel}""", timeout=5)
    data = res.json()
    return data


@worker_shutting_down.connect
def release_task_locks(**kwargs):
    """Warm shutdown 時清除在 worker 中執行的所有 task active 狀態"""
    logging.info("Releasing task locks...")
    active_radios = json.loads(redis_conn.hget(
        active_radios_key, worker_hostname) or '{}')
    for index, key in enumerate(active_radios):
        data = active_radios[key]
        room = data["room"]
        channel = data["channel"]
        lock = get_redis_lock()
        rmap = get_redis_map()
        lock_name = f"{room}-lock-{channel}"
        map_name = f"{room}-map-{channel}"
        rmap.delete(map_name, "playing")
        lock.release(lock_name)
    redis_conn.hdel(active_radios_key, worker_hostname)
    logging.info("Task locks released.")
