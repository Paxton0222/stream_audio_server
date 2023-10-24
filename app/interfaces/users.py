from pydantic import BaseModel

class BaseUser(BaseModel,UserInfo):
    """用戶資料表欄位類型"""
    id: int
    last_login: str # 最後登入日期
    is_deleted: bool
    created_at: str
    updated_at: str
    deleted_at: str

    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    """基本用戶資料"""
    name: str
    email: str
    password: str

class CreateUserInfo(UserInfo):
    """創建用戶需要的資料"""
    pass

class UpdateUserInfo(BaseModel):
    """更新用戶資料所需要的輸入"""
    id: int
    name: str | None = None
    email: str | None = None
