from fastapi.exceptions import HTTPException
from http import HTTPStatus

class BaseError(HTTPException):
    STATUS_CODE = HTTPStatus.NOT_FOUND
    DESC = HTTPStatus.NOT_FOUND
    def __init__(self):
        super().__init__(self.STATUS_CODE, self.DESC)

class UserNotFoundError(BaseError):
    """找不到用戶"""
    STATUS_CODE = HTTPStatus.NOT_FOUND
    DESC = "找不到該用戶"
    RES = {
        "detail": "找不到該用戶"
    }
    DOC = {
        f"{STATUS_CODE}": {
            "description": DESC,
            "content": {
                "application/json": {
                    "example": RES
                }
            }
        }
    }

class DeleteNotSuccessfulError(BaseError):
    """刪除不成功"""
    STATUS_CODE = HTTPStatus.NOT_MODIFIED
    DESC = "刪除未成功"
    RES = None
    DOC = {
        f"{STATUS_CODE}": {
            "description": DESC,
            "content": {
                "application/json": {
                    "example": RES
                }
            }
        }
    }
