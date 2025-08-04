from sqlalchemy import Column, Integer, String
from backend.database import Base

class Staff(Base):
    __tablename__ = "staffs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
