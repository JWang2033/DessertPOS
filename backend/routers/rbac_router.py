# backend/routers/rbac_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, constr
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from backend.database import SessionLocal
from backend.utils.auth_dependencies import require_roles  # 仅 owner 可管理（也可放宽到 manager）
from backend.models.role import Role, Permission, RolePermission, StaffRole
from backend.models.staff import Staff

router = APIRouter(prefix="/rbac", tags=["RBAC Admin"])

# ------------ Common deps ------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

AdminDep = Depends(require_roles(["owner"]))  # 如需店长可管，改成 ["owner", "manager"]

# ------------ Schemas ------------
class PermissionIn(BaseModel):
    code: constr(strip_whitespace=True, min_length=1, max_length=128)
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=128)] = None
    description: Optional[str] = None
    auto_create: bool = False

class PermissionOp(BaseModel):
    code: constr(strip_whitespace=True, min_length=1, max_length=128)

class StaffRolesSet(BaseModel):
    roles: List[constr(strip_whitespace=True, min_length=1, max_length=64)] = Field(default_factory=list)

# ------------ Helpers ------------
def _get_role_by_code(db: Session, code: str) -> Role:
    role = db.execute(select(Role).where(Role.code == code)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role not found: {code}")
    return role

def _get_perm_by_code(db: Session, code: str) -> Permission:
    perm = db.execute(select(Permission).where(Permission.code == code)).scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=404, detail=f"Permission not found: {code}")
    return perm

def _get_staff_or_404(db: Session, staff_id: int) -> Staff:
    staff = db.execute(select(Staff).where(Staff.id == staff_id)).scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff not found: {staff_id}")
    return staff

# ------------ Roles & Permissions ------------
@router.get("/roles", dependencies=[AdminDep])
def list_roles(db: Session = Depends(get_db)):
    rows = db.execute(select(Role)).scalars().all()
    return [
        {"id": r.id, "code": r.code, "name": r.name, "description": r.description}
        for r in rows
    ]

@router.get("/roles/{role_code}/permissions", dependencies=[AdminDep])
def list_role_permissions(role_code: str, db: Session = Depends(get_db)):
    role = _get_role_by_code(db, role_code)
    perms = db.execute(
        select(Permission.code, Permission.name, Permission.description)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .where(RolePermission.role_id == role.id)
    ).all()
    return {
        "role": role.code,
        "permissions": [
            {"code": c, "name": n, "description": d} for (c, n, d) in perms
        ],
    }

@router.post("/roles/{role_code}/permissions:add", dependencies=[AdminDep], status_code=201)
def add_permission_to_role(role_code: str, body: PermissionIn, db: Session = Depends(get_db)):
    role = _get_role_by_code(db, role_code)

    perm = db.execute(select(Permission).where(Permission.code == body.code)).scalar_one_or_none()
    if not perm:
        if body.auto_create:
            perm = Permission(code=body.code, name=body.name or body.code, description=body.description)
            db.add(perm)
            db.commit()
            db.refresh(perm)
        else:
            raise HTTPException(status_code=404, detail=f"Permission not found: {body.code}")

    exists = db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == perm.id
        )
    ).scalar_one_or_none()
    if exists:
        return {"message": "already attached", "role": role.code, "permission": perm.code}

    db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    db.commit()
    return {"message": "attached", "role": role.code, "permission": perm.code}

@router.post("/roles/{role_code}/permissions:remove", dependencies=[AdminDep])
def remove_permission_from_role(role_code: str, body: PermissionOp, db: Session = Depends(get_db)):
    role = _get_role_by_code(db, role_code)
    perm = _get_perm_by_code(db, body.code)

    res = db.execute(
        delete(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == perm.id
        )
    )
    db.commit()
    if res.rowcount == 0:
        return {"message": "no-op (not attached)", "role": role.code, "permission": perm.code}
    return {"message": "detached", "role": role.code, "permission": perm.code}

# ------------ Staff <-> Roles ------------
@router.get("/staff/{staff_id}/roles", dependencies=[AdminDep])
def get_staff_roles(staff_id: int, db: Session = Depends(get_db)):
    _get_staff_or_404(db, staff_id)
    codes = db.execute(
        select(Role.code)
        .join(StaffRole, Role.id == StaffRole.role_id)
        .where(StaffRole.staff_id == staff_id)
    ).scalars().all()
    return {"staff_id": staff_id, "roles": codes}

@router.post("/staff/{staff_id}/roles:set", dependencies=[AdminDep])
def set_staff_roles(staff_id: int, body: StaffRolesSet, db: Session = Depends(get_db)):
    _get_staff_or_404(db, staff_id)

    # 转为集合，避免重复
    new_codes = {c.lower() for c in body.roles}
    # 找到所有角色 id
    roles = db.execute(select(Role).where(Role.code.in_(new_codes))).scalars().all()
    found_codes = {r.code for r in roles}
    missing = sorted(new_codes - found_codes)
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown roles: {missing}")

    # 先删除旧的，再插入新的（替换式）
    db.execute(delete(StaffRole).where(StaffRole.staff_id == staff_id))
    for r in roles:
        db.add(StaffRole(staff_id=staff_id, role_id=r.id))
    db.commit()

    return {"message": "replaced", "staff_id": staff_id, "roles": sorted(found_codes)}

@router.post("/staff/{staff_id}/roles:add", dependencies=[AdminDep])
def add_staff_roles(staff_id: int, body: StaffRolesSet, db: Session = Depends(get_db)):
    _get_staff_or_404(db, staff_id)

    add_codes = {c.lower() for c in body.roles}
    roles = db.execute(select(Role).where(Role.code.in_(add_codes))).scalars().all()
    found_codes = {r.code for r in roles}
    missing = sorted(add_codes - found_codes)
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown roles: {missing}")

    # 查已有
    existing = set(db.execute(
        select(Role.code)
        .join(StaffRole, Role.id == StaffRole.role_id)
        .where(StaffRole.staff_id == staff_id)
    ).scalars().all())

    to_attach = [r for r in roles if r.code not in existing]
    for r in to_attach:
        db.add(StaffRole(staff_id=staff_id, role_id=r.id))
    db.commit()

    final_roles = sorted(existing | {r.code for r in to_attach})
    return {"message": "attached", "staff_id": staff_id, "roles": final_roles}

@router.post("/staff/{staff_id}/roles:remove", dependencies=[AdminDep])
def remove_staff_roles(staff_id: int, body: StaffRolesSet, db: Session = Depends(get_db)):
    _get_staff_or_404(db, staff_id)

    del_codes = {c.lower() for c in body.roles}
    roles = db.execute(select(Role).where(Role.code.in_(del_codes))).scalars().all()
    role_ids = [r.id for r in roles]

    res = db.execute(
        delete(StaffRole).where(
            StaffRole.staff_id == staff_id,
            StaffRole.role_id.in_(role_ids) if role_ids else False  # 空列表保护
        )
    )
    db.commit()

    # 返回最新角色集
    current = db.execute(
        select(Role.code)
        .join(StaffRole, Role.id == StaffRole.role_id)
        .where(StaffRole.staff_id == staff_id)
    ).scalars().all()

    return {
        "message": f"detached ({res.rowcount} row(s))",
        "staff_id": staff_id,
        "roles": sorted(current),
    }
