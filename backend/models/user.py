from sqlalchemy import Column, Integer, String, UniqueConstraint
from backend.database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    prefer_name = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=False, unique=True, index=True)

    __table_args__ = (
        UniqueConstraint("phone_number", name="users_phone"),
    )
