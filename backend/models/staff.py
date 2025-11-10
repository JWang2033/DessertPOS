from sqlalchemy import Column, Integer, String
from backend.database import Base

class Staff(Base):
    __tablename__ = "staffs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    # ⚠️ 过渡期先保留列，建议改成可空，避免以后数据迁移前写入失败
    # role = Column(String(50), nullable=True)   # ← 从原本的 nullable=False 改成 True
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
