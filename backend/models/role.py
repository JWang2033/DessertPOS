# backend/models/role.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from backend.database import Base

# 角色表
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True)   # 例如: 'manager', 'cashier'
    name = Column(String(128), nullable=False)               # 展示名
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

# 权限表
class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(128), nullable=False, unique=True)  # 例如: 'inventory.adjust'
    name = Column(String(128), nullable=False)               # 展示名
    description = Column(String(255))

# 角色-权限 多对多
class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_perm"),
    )

# 员工-角色 多对多（注意引用的是 staffs.id）
class StaffRole(Base):
    __tablename__ = "staff_roles"
    staff_id = Column(Integer, ForeignKey("staffs.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    __table_args__ = (
        UniqueConstraint("staff_id", "role_id", name="uq_staff_role"),
    )

    # 如果在 models/staff.py 与 Role 上用 relationship，取消注释以下两行（非必需）
    # role = relationship("Role", lazy="joined")
    # staff = relationship("Staff", lazy="joined")
