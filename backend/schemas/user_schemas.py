from pydantic import BaseModel

# -------------------
# 输入模型
# -------------------
class UserCreate(BaseModel):
    username: str
    prefer_name: str | None = None
    phone_number: str

# ===== 请求模型（JSON Body 用） =====
class SendCodeRequest(BaseModel):
    phone_number: str

class LoginRequest(BaseModel):
    phone_number: str
    code: str

class RegisterRequest(BaseModel):
    username: str
    prefer_name: str | None = None


# ===== 响应模型 =====
class UserOut(BaseModel):
    id: int
    username: str
    prefer_name: str | None = None
    phone_number: str

    class Config:
        from_attributes = True  # Pydantic v2


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(TokenOut):
    user: UserOut
