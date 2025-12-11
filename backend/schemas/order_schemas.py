# backend/schemas/order_schemas.py
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

# ====== 购物车相关 ======

class ModifierInCart(BaseModel):
    """购物车中的modifier信息"""
    modifier_id: int
    name: str
    type: str
    price: Decimal

    class Config:
        from_attributes = True


class AddToCartRequest(BaseModel):
    """添加商品到购物车的请求"""
    product_id: int
    quantity: int = Field(default=1, ge=1)
    modifiers: List[int] = Field(default_factory=list)  # modifier_id列表


class UpdateCartItemRequest(BaseModel):
    """更新购物车项的请求"""
    quantity: Optional[int] = Field(None, ge=1)
    modifiers: Optional[List[int]] = None


class CartItemOut(BaseModel):
    """购物车项输出"""
    id: str  # Redis中使用字符串ID
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    modifiers: List[ModifierInCart]
    item_subtotal: Decimal  # 该项小计（product_price + sum(modifier_price)) * quantity

    class Config:
        from_attributes = True
class CartOut(BaseModel):
    """购物车输出"""
    items: List[CartItemOut]
    total_price: Decimal  # 购物车总价

    class Config:
        from_attributes = True


# ====== 订单相关 ======

class OrderItemModifierOut(BaseModel):
    """订单项中的modifier输出"""
    modifier_id: int
    modifier_name: str
    modifier_type: str
    modifier_price: Decimal

    class Config:
        from_attributes = True


class OrderItemOut(BaseModel):
    """订单项输出"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    modifiers: List[OrderItemModifierOut]
    price: Decimal

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    """订单输出"""
    id: int
    order_number: str
    user_id: Optional[int]
    total_price: Decimal
    order_status: str
    payment_method: str
    dine_option: str
    items: List[OrderItemOut]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateOrderRequest(BaseModel):
    """创建订单请求（从购物车结算）"""
    payment_method: str = 'cash'  # cash, card, wechat
    dine_option: str = 'take_out'  # take_out, dine_in


# ====== 过敏原相关 ======

class AllergenFilterRequest(BaseModel):
    """过敏原筛选请求"""
    allergens: List[str] = Field(default_factory=list)  # 要排除的过敏原列表
    use_user_setting: bool = False  # 是否使用用户保存的过敏原设置


class UserAllergenOut(BaseModel):
    """用户过敏原输出"""
    allergen: str

    class Config:
        from_attributes = True


class UpdateUserAllergensRequest(BaseModel):
    """更新用户过敏原设置"""
    allergens: List[str]  # 过敏原列表


class ProductWithAllergens(BaseModel):
    """带过敏原信息的产品"""
    id: int
    name: str
    price: Decimal
    type_id: int
    allergens: List[str]  # 该产品包含的过敏原列表

    class Config:
        from_attributes = True
