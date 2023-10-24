from http import HTTPStatus
from fastapi import APIRouter
from app.interfaces import CreateUserInfo, BaseUser, UpdateUserInfo, UpdateUserPassword
from app.exceptions import DeleteNotSuccessfulError, UserNotFoundError
from app import user_service 

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/{id}", responses=UserNotFoundError.DOC)
async def get_user_by_id(id: int) -> BaseUser:
    """使用用戶ID取得用戶資訊"""
    return user_service.get_user_by_id(id)

@router.post("/")
async def register_user(info: CreateUserInfo) -> BaseUser:
    """註冊用戶"""
    return user_service.create_user(info)

@router.put("/info")
async def update_user_info(info: UpdateUserInfo) -> BaseUser:
    """更新用戶資料"""
    return user_service.update_user_by_id(info)

@router.put("/password/")
async def update_user_password(info: UpdateUserPassword) -> BaseUser:
    """更新用戶密碼"""
    return user_service.update_user_password_by_id(info)

@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT, responses=DeleteNotSuccessfulError.DOC)
async def delete_user(id: int):
    """刪除用戶"""
    state = user_service.delete_user_by_id(id)
    print(state)
    if not state:
        raise DeleteNotSuccessfulError()
