from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.env import env_vars

engine = create_engine(f"""{env_vars["DATABASE_TYPE"]}://{env_vars["DATABASE_USER"]}:{env_vars["DATABASE_PASS"]}@{env_vars["DATABASE_HOST"]}:{env_vars["DATABASE_PORT"]}/{env_vars["DATABASE_NAME"]}""",pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)