from pydantic import BaseModel

class StaffCreate(BaseModel):
    username: str
    password: str
    role: str  # 例如 admin、cashier、kitchen 等

class StaffOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True
