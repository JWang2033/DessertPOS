from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.schemas import staff_schemas
from backend.crud import staff_crud
from backend.utils.security import verify_password, create_access_token
from backend.database import SessionLocal
from backend.utils.auth_dependencies import get_current_staff, require_role


from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# User Login
# -------------------------
# @router.post("/login/user")
# def login_user(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db),
# ):
#     user = user_crud.get_user_by_username(db, username=form_data.username)
#     if not user or not verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#     access_token = create_access_token(data={"sub": user.username, "role": "user"})
#     return {"access_token": access_token, "token_type": "bearer"}

# -------------------------
# Staff Login
# -------------------------
@router.post("/login/staff")
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

    # access token
    access_token = create_access_token(data={"sub": staff.username, "role": staff.role})
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------------
# Register New User (Optional)
# -------------------------
# @router.post("/register/user")
# def register_user(
#     user: user_schemas.UserCreate,
#     db: Session = Depends(get_db),
# ):
#     db_user = user_crud.get_user_by_username(db, username=user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")

#     return user_crud.create_user(db=db, user=user)

# -------------------------
# Register New Staff (Optional, with permission)
# -------------------------
@router.post("/register/staff")
def register_staff(
    staff: staff_schemas.StaffCreate,
    db: Session = Depends(get_db),
    current_staff = Depends(require_role(["manager"])), # 必须是manager权限才能注册
):

    # 规范化输入（不改变功能，仅清洗空格/大小写）
    username = staff.username.strip()
    email = staff.email.lower().strip()
    phone = staff.phone.strip()
    full_name = staff.full_name.strip()
    role = staff.role.strip().lower()

    # 角色白名单（按你项目需要可扩展）
    allowed_roles = {"manager", "staff", "trainee"}
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {', '.join(sorted(allowed_roles))}")

    # 去重校验（用户名 / 邮箱 / 手机）
    if staff_crud.get_staff_by_username(db, username=username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if staff_crud.get_staff_by_email(db, email=email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if staff_crud.get_staff_by_phone(db, phone=phone):
        raise HTTPException(status_code=400, detail="Phone already registered")

    # 写回到对象，保持与 crud.create_staff 接口一致
    staff.username = username
    staff.email = email
    staff.phone = phone
    staff.full_name = full_name
    staff.role = role
    print("操作人:", current_staff.full_name)
    print("角色:", current_staff.role)
    return staff_crud.create_staff(db=db, staff=staff)
