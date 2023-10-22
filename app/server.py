from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app import socket_manager
from app.api import api_router
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.websocket("/api/radio/{room}/{channel}")
async def websocket_endpoint(websocket: WebSocket, room: str, channel: int):
    room_id = f"{room}-socket-room-{channel}"
    await socket_manager.add_user_to_room(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await socket_manager.broadcast_to_room(room_id, data)
    except WebSocketDisconnect:  # client disconnect
        await socket_manager.remove_user_from_room(room_id, websocket)
