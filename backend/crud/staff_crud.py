from sqlalchemy.orm import Session
from backend.models.staff import Staff
from backend.schemas.staff_schemas import StaffCreate
from backend.utils.security import get_password_hash

def get_staff_by_username(db: Session, username: str):
    return db.query(Staff).filter(Staff.username == username).first()

def create_staff(db: Session, staff: StaffCreate):
    hashed_password = get_password_hash(staff.password)
    db_staff = Staff(
        username=staff.username,
        password=hashed_password,
        full_name=staff.full_name,
        role=staff.role
    )
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff
