from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.schemas import staff_schemas
from backend.crud import staff_crud
from backend.utils.security import verify_password, create_access_token_v2
from backend.database import SessionLocal
from backend.utils.auth_dependencies import require_roles
from fastapi.security import OAuth2PasswordRequestForm

from backend.models.role import Role, StaffRole  # 现在直接使用 RBAC
RBAC_ENABLED = True   # ← 彻底切 RBAC，不再回退

router = APIRouter(prefix="/staff", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# 1) 员工登录（账号 + 密码）
# ---------------------------------------------------------
# 接口说明：
# 功能：员工使用 username / email / phone 登录后台系统。
# URL：POST /staff/login
# 表单格式（x-www-form-urlencoded）：
#   username=<账号或邮箱或手机>
#   password=<密码>
# 权限：不需要 Authorization（因为是登录接口）
# 返回格式：
#   {
#     "access_token": "<jwt>",
#     "token_type": "bearer"
#   }
# Token sub 格式：sub = "staff:{id}"
# extra_claims 中会包含 roles: ["manager", "cashier", ...]
@router.post("/login")
def login_staff(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    identifier = form_data.username.strip()

    staff = (
        staff_crud.get_staff_by_username(db, username=identifier)
        or staff_crud.get_staff_by_email(db, email=identifier)
        or staff_crud.get_staff_by_phone(db, phone=identifier)
    )
    if not staff or not verify_password(form_data.password, staff.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    role_codes = db.execute(
        select(Role.code)
        .join(StaffRole, Role.id == StaffRole.role_id)
        .where(StaffRole.staff_id == staff.id)
    ).scalars().all()

    access_token = create_access_token_v2(
        subject=f"staff:{staff.id}",
        extra_claims={"roles": role_codes}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------------------------------------------
# 2) 创建员工账号（RBAC 管理）
# ---------------------------------------------------------
# 接口说明：
# 功能：创建新的员工账号（后台管理端）。
# URL：POST /staff/register
# 请求体格式（JSON）：
#   {
#     "username": "alice",
#     "password": "abc123",
#     "full_name": "Alice Tan",
#     "role": "manager",
#     "email": "test@test.com",
#     "phone": "1234567890"
#   }
# 权限：需要 Authorization: Bearer <staff_token>
#       角色要求：owner 或 manager
# 返回格式：
#   {
#     "id": 1,
#     "username": "alice",
#     "full_name": "Alice Tan",
#     "roles": ["manager"]
#   }
@router.post("/register")
def register_staff(
    staff: staff_schemas.StaffCreate,
    db: Session = Depends(get_db),
    # 统一：owner 与 manager 均可创建员工
    current_staff = Depends(require_roles(["owner", "manager"])),
):
    # 规范化输入
    username = staff.username.strip()
    email = staff.email.lower().strip()
    phone = staff.phone.strip()
    full_name = staff.full_name.strip()
    initial_role_code = (staff.role or "staff").strip().lower()

    allowed_roles = {"owner", "manager", "staff", "trainee"}
    if initial_role_code not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {', '.join(sorted(allowed_roles))}")

    # 去重
    if staff_crud.get_staff_by_username(db, username=username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if staff_crud.get_staff_by_email(db, email=email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if staff_crud.get_staff_by_phone(db, phone=phone):
        raise HTTPException(status_code=400, detail="Phone already registered")

    # 写回给 Pydantic 对象（用于 create_staff）
    staff.username = username
    staff.email = email
    staff.phone = phone
    staff.full_name = full_name

    # 创建员工
    new_staff = staff_crud.create_staff(db=db, staff=staff)

    # 绑定角色到 staff_roles
    role_id = db.execute(select(Role.id).where(Role.code == initial_role_code)).scalar_one_or_none()
    if role_id is None:
        raise HTTPException(status_code=400, detail=f"Role not found in RBAC tables: {initial_role_code}")

    db.add(StaffRole(staff_id=new_staff.id, role_id=role_id))
    db.commit()

    return {
        "id": new_staff.id,
        "username": new_staff.username,
        "full_name": new_staff.full_name,
        "roles": [initial_role_code],
    }
