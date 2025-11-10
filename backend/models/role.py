# backend/models/role.py
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    UniqueConstraint,
    BigInteger,   # ← 用 BigInteger 对齐你现有库
    Integer
)
from backend.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    description = Column(String(255))

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(128), nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    description = Column(String(255))

class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(BigInteger, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id"), primary_key=True)
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_perm"),)

class StaffRole(Base):
    __tablename__ = "staff_roles"
    staff_id = Column(Integer, ForeignKey("staffs.id"), primary_key=True)     # staffs.id 是 int
    role_id = Column(BigInteger, ForeignKey("roles.id"), primary_key=True)    # roles.id 是 bigint
    __table_args__ = (UniqueConstraint("staff_id", "role_id", name="uq_staff_role"),)
