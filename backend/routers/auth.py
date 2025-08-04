from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.schemas import staff_schemas
from backend.crud import staff_crud
from backend.utils.security import verify_password, create_access_token
from backend.database import SessionLocal

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
    staff = staff_crud.get_staff_by_username(db, username=form_data.username)
    if not staff or not verify_password(form_data.password, staff.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

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
):
    db_staff = staff_crud.get_staff_by_username(db, username=staff.username)
    if db_staff:
        raise HTTPException(status_code=400, detail="Staff already registered")

    return staff_crud.create_staff(db=db, staff=staff)
