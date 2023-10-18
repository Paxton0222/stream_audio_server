from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from app.env import env_vars
import logging

# 创建数据库引擎
db_url = f"{env_vars['DATABASE_TYPE']}://{env_vars['DATABASE_USER']}:{env_vars['DATABASE_PASS']}@{env_vars['DATABASE_HOST']}:{env_vars['DATABASE_PORT']}/{env_vars['DATABASE_NAME']}"
engine = create_engine(db_url, pool_pre_ping=True)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 declarative base
Base = declarative_base()

try:
    # 尝试创建数据库表格
    Base.metadata.create_all(bind=engine)
except OperationalError as e:
    logging.error(f"Database table creation failed: {e}")
