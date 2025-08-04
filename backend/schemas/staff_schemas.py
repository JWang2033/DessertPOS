from pydantic import BaseModel

class StaffCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str  # e.g., admin, cashier, kitchen, etc.

class StaffOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

    class Config:
        from_attributes = True  # Pydantic v2 用这个替代 orm_mode
