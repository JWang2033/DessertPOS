# backend/routers/test_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from backend.database import SessionLocal, engine, redis_client

router = APIRouter(prefix="/test", tags=["Test Utilities"])

# ---- DB session 复用 ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/ping")
def ping():
    """最基础的健康检查"""
    return {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"}


@router.get("/redis")
def test_redis():
    """Redis 连接+读写测试"""
    try:
        # 1) ping
        pong = redis_client.ping()
        # 2) set/get 一个 5 秒的测试键
        redis_client.set("test:hello", "world", ex=5)
        val = redis_client.get("test:hello")
        ttl = redis_client.ttl("test:hello")
        return {
            "connected": pong is True,
            "get": val,
            "ttl_seconds": ttl,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/mysql")
def test_db_raw():
    """MySQL 原始连接 & SELECT 1"""
    try:
        with engine.connect() as conn:
            one = conn.execute(text("SELECT 1")).scalar()
            version = conn.execute(text("SELECT VERSION()")).scalar()
        return {"connected": one == 1, "version": version}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/db/session")
def test_db_session(db: Session = Depends(get_db)):
    """通过 Session 执行一个简单语句"""
    try:
        result = db.execute(text("SELECT DATABASE()")).scalar()
        return {"connected": True, "database": result}
    except Exception as e:
        return {"connected": False, "error": str(e)}
