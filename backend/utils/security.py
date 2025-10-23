# backend/utils/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status


# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用于签名 JWT 的密钥与算法
SECRET_KEY = "your-secret-key"  # 请在生产环境使用安全保密的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # token 有效期（分钟）

# 加密密码

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 创建 JWT token
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 解码 JWT token（可用于后续鉴权中间件）
def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# 从header解码
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """作为 FastAPI 依赖使用：从请求头读取 Bearer Token 并解码"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )