from sqlalchemy import Integer, Column, String, DateTime 
from datetime import datetime

from app.sql import Base
from app.models.soft_delete import SoftDeleteMixin
from app.models.mixin import ModelMixin

class User(Base,SoftDeleteMixin, ModelMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, comment='姓名', nullable=False)  # 用户姓名
    email = Column(String(255), unique=True, index=True,nullable=False, comment='电子邮件')  # 电子邮件
    password = Column(String(255), comment="用戶密碼",nullable=False)
    created_at = Column(DateTime, default=datetime.now,comment='创建日期')  # 创建日期
    updated_at = Column(DateTime, onupdate=datetime.now,comment='最后更新日期')  # 最后更新日期
    last_login = Column(DateTime, comment='最后登录时间', default=datetime.now)  # 最后登录时间