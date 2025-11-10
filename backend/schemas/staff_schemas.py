# backend/schemas/staff_schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr
from typing import Optional, List, Literal

# 创建员工时的请求体：是否允许指定“初始角色”
# - 如果你只允许后台逻辑统一给 "staff"，可以把 initial_role_code 去掉
class StaffCreate(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    password: constr(min_length=6, max_length=128)
    full_name: constr(strip_whitespace=True, min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[constr(strip_whitespace=True, max_length=20)] = None
    # 过渡期如需前端传一个初始角色，用下面这行；完全 RBAC 后也可以保留
    initial_role_code: Optional[Literal["owner","manager","staff","trainee"]] = "staff"

class StaffOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    # 对齐 RBAC：返回多角色
    roles: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
