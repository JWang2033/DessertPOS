# backend/schemas/user_schemas.py
from pydantic import BaseModel, constr

class StartLoginRequest(BaseModel):
    phone_number: constr(min_length=4, max_length=20)

class StartLoginResponse(BaseModel):
    exists: bool
    otp_ttl: int
    resend_after: int

class VerifyRequest(BaseModel):
    phone_number: constr(min_length=4, max_length=20)
    code: constr(min_length=4, max_length=6)
    # 新用户用到；老用户可不传
    username: constr(min_length=1, max_length=50) | None = None
    prefer_name: constr(max_length=50) | None = None

class UserOut(BaseModel):
    id: int
    username: str
    phone_number: str
    prefer_name: str | None = None
    access_token: str
    class Config:
        from_attributes = True
