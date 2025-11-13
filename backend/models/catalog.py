# backend/models/catalog.py
from sqlalchemy import (
    Column, Integer, BigInteger, String, DECIMAL, Enum, JSON, DateTime, TIMESTAMP,
    ForeignKey, text
)
from sqlalchemy.dialects.mysql import TINYINT
from backend.database import Base

# ============ 基础表（与现有表结构一致） ============

class ProductType(Base):
    __tablename__ = "product_types"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False, server_default=text("0.00"))
    type_id = Column(BigInteger, nullable=False)  # 指向 product_types.id（逻辑外键）
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class Modifier(Base):
    __tablename__ = "modifiers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # 例: "size" / "sugar" / "ice" / "addon"
    price = Column(DECIMAL(10, 2), nullable=False, server_default=text("0.00"))
    is_active = Column(TINYINT, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class ModifierProduct(Base):
    __tablename__ = "modifier_product"
    product_id = Column(BigInteger, primary_key=True)
    modifier_id = Column(BigInteger, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    unit = Column(String(16), nullable=False)
    quantity_remaining = Column(DECIMAL(12, 3), nullable=False, server_default=text("0.000"))
    safety_stock = Column(DECIMAL(12, 3), nullable=False, server_default=text("0.000"))
    status = Column(TINYINT, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class SemiFinished(Base):
    __tablename__ = "semifinished"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    unit = Column(String(16), nullable=False)
    quantity_remaining = Column(DECIMAL(12, 3), nullable=False, server_default=text("0.000"))
    safety_stock = Column(DECIMAL(12, 3), nullable=False, server_default=text("0.000"))
    status = Column(TINYINT, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class ProductIngredient(Base):
    __tablename__ = "product_ingredients"
    product_id = Column(BigInteger, primary_key=True)
    ingredient_id = Column(BigInteger, primary_key=True)
    amount_per_unit = Column(DECIMAL(12, 3), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class ProductSemiFinished(Base):
    __tablename__ = "product_semifinished"
    product_id = Column(BigInteger, primary_key=True)
    semifinished_id = Column(BigInteger, primary_key=True)
    amount_per_unit = Column(DECIMAL(12, 3), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
