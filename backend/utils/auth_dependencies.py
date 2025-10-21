# backend/utils/auth_dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from backend.database import SessionLocal
from backend.crud import staff_crud
from backend.utils.security import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session
from typing import Iterable


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/staff")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_staff(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    staff = staff_crud.get_staff_by_username(db, username=username)
    if staff is None:
        raise credentials_exception
    return staff

def require_role(roles: Iterable[str]):
    """
    依赖工厂：检查当前登录用户是否属于给定角色之一。
    用法：Depends(require_role(["manager", "kitchen"]))
    """
    roles_set = set(r.lower() for r in roles)

    def checker(current_staff = Depends(get_current_staff)):
        if current_staff.role.lower() not in roles_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges: requires one of {sorted(roles_set)}"
            )
        return current_staff  # 可在路由中继续使用当前用户
    return checker