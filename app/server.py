from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from app.redis import RedisQueue, RedisLock, RedisMap, get_redis_queue, get_redis_lock, get_redis_map
from app.services.room import RoomService
from fastapi.middleware.cors import CORSMiddleware
from app import socket_manager
from app.api import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.websocket("/api/radio/{room}/{channel}")
async def websocket_endpoint(websocket: WebSocket, room: str, channel: int, redis_lock: RedisLock = Depends(get_redis_lock), redis_queue: RedisQueue = Depends(get_redis_queue), redis_map: RedisMap = Depends(get_redis_map)):
    room_id = f"{room}-socket-room-{channel}"
    room_name = f"{room}-room-{channel}"
    await socket_manager.add_user_to_room(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await socket_manager.broadcast_to_room(room_id, data)
    except WebSocketDisconnect:  # client disconnect
        await socket_manager.remove_user_from_room(room_id, websocket)
