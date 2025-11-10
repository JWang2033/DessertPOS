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
