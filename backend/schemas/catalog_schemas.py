# backend/schemas/catalog_schemas.py
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from decimal import Decimal

# ====== 公共 ======
class ProductBase(BaseModel):
    name: str
    price: Decimal = Field(default=Decimal("0.00"))
    type_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    type_id: Optional[int] = None

class ProductOut(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductDetail(ProductOut):
    modifiers: List["ModifierOut"] = []

class ModifierBase(BaseModel):
    name: str
    type: str
    price: Decimal = Field(default=Decimal("0.00"))
    is_active: int = 1

class ModifierCreate(ModifierBase):
    pass

class ModifierUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[int] = None

class ModifierOut(ModifierBase):
    id: int
    class Config:
        from_attributes = True

class ProductTypeBase(BaseModel):
    name: str

class ProductTypeCreate(ProductTypeBase):
    pass

class ProductTypeOut(ProductTypeBase):
    id: int
    class Config:
        from_attributes = True

# 查询参数（前台用）
class ProductQuery(BaseModel):
    categoryId: Optional[int] = None   # 对应 type_id
    # 预留：allergen_not_in（暂无映射表，这里先保留参数以便未来拓展）
    allergen_not_in: Optional[str] = None

# 关联请求
class AttachModifierRequest(BaseModel):
    modifier_id: int

# 反向引用修复
ProductDetail.model_rebuild()
