from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app import socket_service, room_service, tube_service

router = APIRouter(prefix="/stream", tags=["stream"])

@router.post("/add/{room}/{channel}")
async def stream_add(room: str, channel: int, url: str):
    """加入直播歌曲"""
    info = tube_service.info(url)
    return room_service.add(info,room,channel)

@router.post("/play/{room}/{channel}")
async def stream_play(room: str, channel: int):  # 如果當前線程沒有在播放
    """直撥開始"""
    return room_service.play(room,channel)

@router.post("/pause/{room}/{channel}")
async def stream_pause(room: str, channel: int):
    """直播暫停"""
    return room_service.pause(room,channel)

@router.get("/state/{room}/{channel}")
async def stream_state(room: str, channel: int):
    """直播狀態"""
    state = room_service.is_playing(room,channel)
    return {
        "status": state,
        "task_id": room_service.get_playing_task_id(room,channel),
        "data": room_service.playing_data(room,channel) if state else {}
    }

@router.post("/next/{room}/{channel}")
async def stream_next(room: str, channel: int):
    """下一首"""
    return room_service.next(room,channel)

@router.get("/list/{room}/{channel}")
async def stream_list(room: str, channel: int, page: int, limit: int):
    """直播等待列表"""
    return room_service.list(page, limit,room,channel)


@router.get("/list/length/{room}/{channel}")
async def stream_length(room: str, channel: int):
    """直播等待列表總長度"""
    return room_service.length(room,channel)


@router.websocket("/{room}/{channel}")
async def websocket_endpoint(websocket: WebSocket, room: str, channel: int):
    """Stream notification websocket endpoint"""
    room_id = f"{room}-socket-room-{channel}"
    await socket_service.add_user_to_room(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await socket_service.broadcast_to_room(room_id, data)
    except WebSocketDisconnect:  # client disconnect
        await socket_service.remove_user_from_room(room_id, websocket)
