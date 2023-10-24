from fastapi.exceptions import HTTPException
from http import HTTPStatus

class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(HTTPStatus.NOT_FOUND, "找不到該用戶")
