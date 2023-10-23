from sqlalchemy import Integer, Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.sql import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, comment='姓名')  # 用户姓名
    created_at = Column(DateTime, server_default=func.now(),
                        comment='创建日期')  # 创建日期
    updated_at = Column(DateTime, onupdate=func.now(),
                        comment='最后更新日期')  # 最后更新日期
    last_login = Column(DateTime, comment='最后登录时间')  # 最后登录时间
    email = Column(String(255), unique=True, index=True,
                   nullable=False, comment='电子邮件')  # 电子邮件
    nickname = Column(String(255), comment='用户昵称')  # 用户昵称
    is_deleted = Column(Boolean, default=False, comment='软删除标志')  # 软删除标志
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')  # 删除时间

    def delete(self):
        self.is_deleted = True
        self.deleted_at = func.now()
