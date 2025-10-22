from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from backend.models.user import User

def get_user_by_phone(db: Session, phone: str) -> User | None:
    return db.query(User).filter(User.phone_number == phone).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, username: str, phone_number: str, prefer_name: str | None = None) -> User:
    user = User(
        username=username,
        phone_number=phone_number,
        prefer_name=prefer_name
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # 与唯一约束冲突时抛出更友好的错误
        raise HTTPException(status_code=400, detail="Phone number already registered")
    db.refresh(user)
    return user
