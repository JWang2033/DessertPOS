from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal, redis_client
from backend.crud import user_crud
from backend.utils.security import create_access_token
from backend.schemas.user_schemas import (
    SendCodeRequest, LoginRequest, RegisterRequest,
    UserOut, LoginResponse
)
from backend.utils.security import get_current_token_payload  # 依赖：从 Authorization 头取 token

router = APIRouter(prefix="/user", tags=["User"])

# DB 依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# 1) 发送验证码（JSON）
# ------------------------
@router.post("/send-code")
def send_verification_code(payload: SendCodeRequest, db: Session = Depends(get_db)):
    phone = payload.phone_number.strip()

    # 生成 6 位验证码并存入 Redis（5 分钟）
    import random
    code = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{phone}", 300, code)

    # 若用户不存在，创建占位用户（可按需保留/去掉）
    user = user_crud.get_user_by_phone(db, phone)
    if not user:
        user_crud.create_user(db, phone_number=phone, username=f"user_{phone[-4:]}")

    # 正式环境在此调用短信网关；现在直接返回方便测试
    return {"message": "Verification code sent", "debug_code": code}


# ------------------------
# 2) 登录（JSON）
# ------------------------
@router.post("/login", response_model=LoginResponse)
def login_with_code(payload: LoginRequest, db: Session = Depends(get_db)):
    phone = payload.phone_number.strip()
    code = payload.code.strip()

    stored_code = redis_client.get(f"otp:{phone}")
    if not stored_code:
        raise HTTPException(status_code=400, detail="Verification code expired or not found")
    if stored_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user = user_crud.get_user_by_phone(db, phone)
    if not user:
        user = user_crud.create_user(db, phone_number=phone)

    # 生成 token，并删除验证码避免复用
    token = create_access_token({"sub": phone, "role": "user"})
    redis_client.delete(f"otp:{phone}")

    return {"access_token": token, "token_type": "bearer", "user": user}


# ------------------------
# 3) 注册补全（JSON + Bearer Token）
# ------------------------
@router.post("/register", response_model=UserOut)
def register_user(
    payload: RegisterRequest,
    token_data: dict = Depends(get_current_token_payload),  # 从 Authorization 头读取并解码 token
    db: Session = Depends(get_db),
):
    phone = token_data.get("sub")
    if not phone:
        raise HTTPException(status_code=401, detail="Invalid credential")

    user = user_crud.get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = payload.username.strip()
    user.prefer_name = payload.prefer_name.strip() if payload.prefer_name else None

    db.commit()
    db.refresh(user)
    return user
