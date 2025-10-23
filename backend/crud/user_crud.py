from sqlalchemy.orm import Session
from backend.models.user import User

def get_user_by_phone(db: Session, phone_number: str):
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, username: str, phone_number: str, prefer_name: str | None = None):
    user = User(username=username, phone_number=phone_number, prefer_name=prefer_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
