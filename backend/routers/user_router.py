# backend/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import SessionLocal, redis_client
from backend.crud import user_crud
from backend.schemas.user_schemas import (
    SendCodeRequest, LoginRequest, RegisterRequest,
    UserOut, LoginResponse
)

# ✅ 与 staff 同步的安全依赖：使用 v2 token、oauth2_user、parse_subject
from backend.utils.security import (
    create_access_token_v2,
    get_current_user_payload,
    parse_subject,
)

router = APIRouter(prefix="/user", tags=["User"])

# ------------------------
# DB 依赖
# ------------------------
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

    # 生成 6 位验证码并存入 Redis（有效期 5 分钟）
    import random
    code = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{phone}", 300, code)

    # 若用户不存在，创建占位用户（保持原有行为）
    user = user_crud.get_user_by_phone(db, phone)
    if not user:
        user_crud.create_user(db, phone_number=phone, username=f"user_{phone[-4:]}")

    # 生产环境应调用短信服务，这里返回 debug_code 方便测试
    return {"message": "Verification code sent", "debug_code": code}

# ------------------------
# 2) 登录（JSON）
#    ⚠️ 改为 v2 JWT：sub = "user:{id}"
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
        user = user_crud.create_user(db, phone_number=phone, username=f"user_{phone[-4:]}")

    # ✅ v2 签发：用用户 ID 作为 subject
    # 额外声明可按需添加（例如 {"aud": "user"} 或 {"roles": ["customer"]}）
    token = create_access_token_v2(subject=f"user:{user.id}")

    # 避免验证码复用
    redis_client.delete(f"otp:{phone}")

    return {"access_token": token, "token_type": "bearer", "user": user}

# ------------------------
# 3) 注册补全（JSON + Bearer Token）
#    ⚠️ 用 get_current_user_payload + parse_subject 解析 "user:{id}"
# ------------------------
@router.post("/register", response_model=UserOut)
def register_user(
    payload: RegisterRequest,
    token_data: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    kind, user_id = parse_subject(token_data.get("sub", ""))
    if kind != "user":
        raise HTTPException(status_code=401, detail="Token not for user")

    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        # 理论上不应发生：token 中 id 对应的用户应该存在
        raise HTTPException(status_code=404, detail="User not found")

    user.username = payload.username.strip()
    user.prefer_name = payload.prefer_name.strip() if payload.prefer_name else None

    db.commit()
    db.refresh(user)
    return user