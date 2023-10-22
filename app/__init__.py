from app.models import Users
from app.services.socket import WebSocketManager

socket_manager = WebSocketManager()

__all__ = (
    Users,
    socket_manager
)
