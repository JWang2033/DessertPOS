from sqlalchemy import Column, Integer, String
from database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="staff")  # 可选值如 "staff", "admin"
