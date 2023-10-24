from pydantic import BaseModel, EmailStr, constr, conint
from typing import Optional
from datetime import datetime

class UserInfo(BaseModel):
    """基本用戶資料"""
    name: constr(min_length=1, max_length=255)
    email: EmailStr
    password: constr(min_length=1, max_length=255)

class BaseUser(UserInfo):
    """用戶欄位資料類型"""
    id: conint(gt=0)
    last_login: datetime # 最後登入日期
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True

class CreateUserInfo(UserInfo):
    """創建用戶需要的資料"""

class UpdateUserInfo(BaseModel):
    """更新用戶資料所需要的輸入"""
    id: conint(gt=0)
    name: Optional[constr(min_length=1,max_length=255)]
    email: Optional[constr(min_length=1,max_length=255)]

class UpdateUserPassword(BaseModel):
    """用戶修改密碼"""
    id: conint(gt=0)
    password: constr(min_length=1,max_length=255)
