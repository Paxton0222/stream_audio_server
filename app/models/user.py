from sqlalchemy import Integer, Column, String
from app.sql import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True)