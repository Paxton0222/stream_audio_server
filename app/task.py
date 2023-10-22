from app.celery import celery
from app.stream import Stream
from app.redis import get_redis_lock, get_redis_map
from celery.signals import worker_shutting_down
from app.env import env_vars
from app.redis import redis_conn
import json
import signal
import logging
import asyncio
import websockets
import requests
import os
import socket  # 导入 socket 模块

# 获取 worker 主机名
worker_hostname = socket.gethostname()

# 创建带有主机名前缀的 active_radios 的键
active_radios_key = f'active_radios'


@celery.task
def live_stream_youtube_audio(info: dict, room: str, channel: int):
    lock = get_redis_lock()
    rmap = get_redis_map()
    room_name = f"{room}-room-{channel}"
    lock_name = f"{room}-lock-{channel}"
    map_name = f"{room}-map-{channel}"
    stream = Stream()
    process = None
    terminate = False

    async def connect_to_websocket_server(event: str):
        uri = f"""{env_vars["WEBSOCKET_URL"]}/api/radio/{room}/{channel}"""
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

    asyncio.get_event_loop().run_until_complete(connect_to_websocket_server("play"))

    def release_lock(signum=None, frame=None):
        rmap.delete(map_name, "playing")
        lock.release(lock_name)
        logging.info(f"{room_name} released lock successfully.")

    def terminate_process(signum, frame):
        nonlocal process, terminate
        terminate = True
        if process:
            logging.info(f"{room_name} terminating process...")
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                logging.info(f"{room_name} terminated process successfully.")
            except ProcessLookupError:
                logging.error(f"{room_name} Failed to terminate process.")

    signal.signal(signal.SIGTERM, terminate_process)

    try:
        logging.info(f"Room {room_name} playing music: {info['title']}")

        active_radios = json.loads(redis_conn.hget(
            active_radios_key, worker_hostname) or '{}')
        active_radios[room_name] = {
            "room": room,
            "channel": channel
        }
        logging.info(active_radios)
        redis_conn.hset(active_radios_key, worker_hostname,
                        json.dumps(active_radios))

        process = stream.live_stream_audio(
            info["url"], f"""{env_vars["RTMP_TARGET"]}/{room_name}""", False)
        process.wait()
        logging.info(f"Room {room_name} music ended: {info['title']}")
    except Exception as e:
        logging.error(e)
    finally:
        release_lock()
        active_radios = json.loads(redis_conn.hget(
            active_radios_key, worker_hostname) or '{}')
        del active_radios[room_name]
        redis_conn.hset(active_radios_key, worker_hostname,
                        json.dumps(active_radios))
        logging.info(active_radios)
        asyncio.get_event_loop().run_until_complete(
            connect_to_websocket_server("pause"))
        if not terminate:
            live_stream_next_youtube_audio.apply_async(
                args=(room, channel), retry=False, expire=5)
        logging.info(f"{room_name} end of script")


@celery.task
def live_stream_next_youtube_audio(room: str, channel: int):
    res = requests.post(
        f"""{env_vars["BACKEND_URL"]}/api/stream/next/{room}/{channel}""", timeout=5)
    data = res.json()
    room_name = f"{room}-room-{channel}"
    active_radios = json.loads(redis_conn.hget(
        active_radios_key, room_name) or '{}')
    active_radios[room_name] = {
        "room": room,
        "channel": channel
    }
    redis_conn.hset(active_radios_key, room_name,
                    json.dumps(active_radios))
    return data


@worker_shutting_down.connect
def release_task_locks(**kwargs):
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
