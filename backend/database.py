# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import redis

# ------------------------------
# MySQL 配置
# ------------------------------
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:WYz%40Dessert2025@localhost:3307/dessert_pos"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ------------------------------
# Redis 配置
# ------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# decode_responses=True 保证返回 str 而不是 bytes
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
