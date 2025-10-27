from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.schemas import staff_schemas
from backend.crud import staff_crud
from backend.utils.security import verify_password, create_access_token_v2
from backend.database import SessionLocal
from backend.utils.auth_dependencies import require_role  # 兼容期仍按老的“manager”角色校验

# ✅ 若你已创建 RBAC 表，可用以下模型做角色查询/绑定（若未创建，也不会报错，只需注释掉用到的代码块）
try:
    from backend.models.role import Role, StaffRole  # 新 RBAC 表
    RBAC_ENABLED = True
except Exception:
    RBAC_ENABLED = False

from backend.utils.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/staff", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Staff Login
# -------------------------
@router.post("/login")
def login_staff(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    identifier = form_data.username.strip()  # 用户输入的登录标识

    # 依次匹配用户名、邮箱、手机号
    staff = (
        staff_crud.get_staff_by_username(db, username=identifier)
        or staff_crud.get_staff_by_email(db, email=identifier)
        or staff_crud.get_staff_by_phone(db, phone=identifier)
    )

    # verify
    if not staff or not verify_password(form_data.password, staff.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 查角色 codes（优先 RBAC 表；没有则回退旧字段）
    role_codes = []
    if RBAC_ENABLED:
        role_codes = db.execute(
            select(Role.code)
            .join(StaffRole, Role.id == StaffRole.role_id)
            .where(StaffRole.staff_id == staff.id)
        ).scalars().all()
    if not role_codes:
        # 兼容期回退：若仍有 staff.role 字段
        role_attr = getattr(staff, "role", None)
        if role_attr:
            role_codes = [role_attr.lower()]

    # 签发基于 ID 的 token，并把 roles 放进去（前端 UI 可用；后端仍以查库为准）
    access_token = create_access_token_v2(
        subject=f"staff:{staff.id}",
        extra_claims={"roles": role_codes}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------------
# Register New Staff (with permission)
# -------------------------
@router.post("/register")
def register_staff(
    staff: staff_schemas.StaffCreate,
    db: Session = Depends(get_db),
    current_staff = Depends(require_role(["manager"])),  # 兼容期：必须是 manager 才能注册
):
    # 规范化输入
    username = staff.username.strip()
    email = staff.email.lower().strip()
    phone = staff.phone.strip()
    full_name = staff.full_name.strip()
    initial_role_code = (staff.role or "staff").strip().lower()  # 作为“初始角色代码”

    # 角色白名单（过渡期保持不变）
    allowed_roles = {"manager", "staff", "trainee"}
    if initial_role_code not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {', '.join(sorted(allowed_roles))}")

    # 去重校验
    if staff_crud.get_staff_by_username(db, username=username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if staff_crud.get_staff_by_email(db, email=email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if staff_crud.get_staff_by_phone(db, phone=phone):
        raise HTTPException(status_code=400, detail="Phone already registered")

    # 写回到对象，保持与 crud.create_staff 接口一致（兼容旧结构：仍给 staff.role 赋值）
    staff.username = username
    staff.email = email
    staff.phone = phone
    staff.full_name = full_name
    staff.role = initial_role_code  # ✅ 兼容期：保留写入；未来删除 staffs.role 后可移除

    # 创建员工
    new_staff = staff_crud.create_staff(db=db, staff=staff)

    # ✅ 如果 RBAC 表已存在：同步到 staff_roles（正式做法）
    if RBAC_ENABLED:
        role_obj = db.execute(select(Role).where(Role.code == initial_role_code)).scalar_one_or_none()
        if role_obj is None:
            raise HTTPException(status_code=400, detail=f"Role not found in RBAC tables: {initial_role_code}")
        db.add(StaffRole(staff_id=new_staff.id, role_id=role_obj.id))
        db.commit()

    return {
        "id": new_staff.id,
        "username": new_staff.username,
        "full_name": new_staff.full_name,
        "roles": [initial_role_code],  # 返回 roles 列表（即使还在过渡期）
    }
