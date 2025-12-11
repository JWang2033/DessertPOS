# backend/models/order.py
from sqlalchemy import (
    Column, Integer, BigInteger, String, DECIMAL, Enum as SQLEnum, JSON, DateTime, TIMESTAMP,
    ForeignKey, Text, text
)
from sqlalchemy.dialects.mysql import TINYINT
from backend.database import Base

class Order(Base):
    """订单主表"""
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_number = Column(String(32), nullable=False, unique=True, index=True)  # 订单号
    user_id = Column(Integer, nullable=True)  # 关联 Users 表，可为空（匿名下单）
    pickup_number = Column(String(16), nullable=True)  # 取餐号
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)
    payment_method = Column(SQLEnum('cash', 'card', 'wechat', name='payment_method_enum'), nullable=False)
    dine_option = Column(SQLEnum('take_out', 'dine_in', name='dine_option_enum'), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("0.00"))
    order_status = Column(SQLEnum('IP', 'Completed', 'Refunded', 'preorder', name='order_status_enum'), nullable=False, server_default=text("'IP'"), index=True)


class OrderItem(Base):
    """订单明细表 - 存储订单中的每个产品"""
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(BigInteger, nullable=False, index=True)  # 关联 products 表
    quantity = Column(Integer, nullable=False, server_default=text("1"))
    modifiers = Column(JSON, nullable=True)  # 存储modifier信息的JSON
    price = Column(DECIMAL(10, 2), nullable=False)  # 该项总价（含modifier）
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


# OrderItemModifier is not used - modifiers are stored as JSON in order_items.modifiers


class Cart(Base):
    """购物车主表 - 每个用户一个购物车"""
    __tablename__ = "carts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)  # 关联 Users 表
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)


class CartItem(Base):
    """购物车项目表"""
    __tablename__ = "cart_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cart_id = Column(BigInteger, ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(BigInteger, nullable=False)  # 关联 products 表
    quantity = Column(Integer, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)


class CartItemModifier(Base):
    """购物车项目的Modifier"""
    __tablename__ = "cart_item_modifiers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cart_item_id = Column(BigInteger, ForeignKey("cart_items.id"), nullable=False, index=True)
    modifier_id = Column(BigInteger, nullable=False)  # 关联 modifiers 表
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class UserAllergen(Base):
    """用户过敏原设置表"""
    __tablename__ = "user_allergens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False, index=True)
    allergen = Column(String(50), nullable=False)  # 过敏原名称，如 "milk", "nuts", "gluten"
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class ProductAllergen(Base):
    """产品过敏原关联表"""
    __tablename__ = "product_allergens"

    product_id = Column(BigInteger, ForeignKey("products.id"), primary_key=True)
    allergen = Column(String(50), primary_key=True)  # 过敏原名称
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
