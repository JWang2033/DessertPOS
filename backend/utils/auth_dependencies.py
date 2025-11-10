# backend/utils/auth_dependencies.py
from typing import Iterable, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.database import SessionLocal
from backend.crud import staff_crud

# ✅ 使用 security.py 提供的解析依赖与 subject 解析（sub = "staff:{id}"）
from backend.utils.security import (
    get_current_staff_payload,  # 读取并校验员工端 Bearer Token（绑定 /staff/login）
    parse_subject,              # 解析 "staff:{id}"
)

# RBAC 模型
from backend.models.role import StaffRole, Role, RolePermission, Permission


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
# 当前登录员工对象（基于 sub=staff:{id}）
# ------------------------
def get_current_staff(
    payload: Dict[str, Any] = Depends(get_current_staff_payload),
    db: Session = Depends(get_db),
):
    kind, sid = parse_subject(payload.get("sub", ""))
    if kind != "staff":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not for staff")

    staff = getattr(staff_crud, "get_staff_by_id", None)
    if not callable(staff):
        raise HTTPException(status_code=500, detail="get_staff_by_id not implemented in staff_crud")
    staff = staff_crud.get_staff_by_id(db, staff_id=sid)
    if staff is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Staff not found")
    return staff


# ------------------------
# 角色检查（兼容旧字段 + 新表）
# 用法：Depends(require_roles(["manager"])) 或 ["owner","manager"]
# ------------------------
def require_roles(roles: Iterable[str]):
    roles_set = {r.lower() for r in roles}

    def checker(current=Depends(get_current_staff), db: Session = Depends(get_db)):
        # 1) 兼容旧 staffs.role（如果仍存在）
        role_attr = getattr(current, "role", None)
        if role_attr and role_attr.lower() in roles_set:
            return current

        # 2) 新 RBAC：staff_roles -> roles
        codes = set(
            db.execute(
                select(Role.code)
                .join(StaffRole, Role.id == StaffRole.role_id)
                .where(StaffRole.staff_id == current.id)
            ).scalars().all()
        )
        if codes & roles_set:
            return current

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires one of roles: {sorted(roles_set)}"
        )

    return checker


# ------------------------
# 权限检查（推荐）
# 用法：Depends(requires("staff.manage")) / Depends(requires("inventory.adjust"))
# ------------------------
def requires(*perms_required: str):
    required = set(perms_required)

    def checker(current=Depends(get_current_staff), db: Session = Depends(get_db)):
        owned = set(
            db.execute(
                select(Permission.code)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .join(StaffRole, RolePermission.role_id == StaffRole.role_id)
                .where(StaffRole.staff_id == current.id)
            ).scalars().all()
        )
        # 可选特权：owner 角色通常映射到 admin.*（全权限）
        if "admin.*" in owned or required.issubset(owned):
            return current

        missing = list(required - owned)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {missing}"
        )

    return checker


# 兼容别名：让旧代码 `from ... import require_role` 仍然可用
require_role = require_roles
