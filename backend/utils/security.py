# backend/utils/security.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from typing import Any, Dict, Optional, Tuple, List
import uuid


# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用于签名 JWT 的密钥与算法
SECRET_KEY = "your-secret-key"  # 请在生产环境使用安全保密的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # token 有效期（分钟）


def _utcnow():
    # 统一使用带时区的时间戳
    from datetime import datetime
    return datetime.now(tz=timezone.utc)

# 加密密码

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 为了与现有 oauth2_scheme 并存，我们新增两套更明确的 OAuth2：
oauth2_user = OAuth2PasswordBearer(tokenUrl="/user/login")
oauth2_staff = OAuth2PasswordBearer(tokenUrl="/staff/login")

# 创建 JWT token
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def create_access_token_v2(
    subject: str,                 # 形如 "staff:123" 或 "user:45"
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    更规范的 token 发行器：
    - 用 ID 做 sub：'staff:{id}' / 'user:{id}'
    - 可附加 extra_claims（例如 roles）
    - 使用你现有的 SECRET_KEY / ALGORITHM / ACCESS_TOKEN_EXPIRE_MINUTES
    """
    now = _utcnow()
    exp = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "typ": "access",
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# 解码 JWT token（可用于后续鉴权中间件）
def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# 从header解码
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def decode_token_v2(token: str) -> Dict[str, Any]:
    """
    更健壮的解码（保留你原来的 decode_access_token，不互相影响）
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require_exp": True})
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )

def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """作为 FastAPI 依赖使用：从请求头读取 Bearer Token 并解码"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

def get_current_user_payload(token: str = Depends(oauth2_user)) -> Dict[str, Any]:
    """用户端：从 Authorization: Bearer 里解码 payload"""
    return decode_token_v2(token)

def get_current_staff_payload(token: str = Depends(oauth2_staff)) -> Dict[str, Any]:
    """员工端：从 Authorization: Bearer 里解码 payload"""
    return decode_token_v2(token)

def parse_subject(sub: str) -> Tuple[str, int]:
    """
    'staff:123' -> ('staff', 123)
    'user:45'   -> ('user', 45)
    """
    if ":" not in sub:
        raise HTTPException(status_code=401, detail="Malformed subject")
    kind, id_str = sub.split(":", 1)
    try:
        return kind, int(id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed subject id")

def get_current_staff_id(payload: Dict[str, Any] = Depends(get_current_staff_payload)) -> int:
    kind, sid = parse_subject(payload.get("sub", ""))
    if kind != "staff":
        raise HTTPException(status_code=401, detail="Token not for staff")
    return sid

def get_current_user_id(payload: Dict[str, Any] = Depends(get_current_user_payload)) -> int:
    kind, uid = parse_subject(payload.get("sub", ""))
    if kind != "user":
        raise HTTPException(status_code=401, detail="Token not for user")
    return uid
