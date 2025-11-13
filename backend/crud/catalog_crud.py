# backend/crud/catalog_crud.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from backend.models.catalog import (
    Product, ProductType, Modifier, ModifierProduct
)

def list_categories(db: Session) -> List[ProductType]:
    stmt = select(ProductType).order_by(ProductType.id.asc())
    return db.execute(stmt).scalars().all()

def list_products(
    db: Session,
    category_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Product]:
    conditions = []
    if category_id:
        conditions.append(Product.type_id == category_id)

    stmt = select(Product).where(and_(*conditions) if conditions else True)\
        .order_by(Product.id.asc())\
        .limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()

def get_product(db: Session, product_id: int) -> Optional[Product]:
    stmt = select(Product).where(Product.id == product_id)
    return db.execute(stmt).scalar_one_or_none()

def get_product_modifiers(db: Session, product_id: int) -> List[Modifier]:
    # 只返回 is_active=1 的 modifier
    j = select(Modifier).join(
        ModifierProduct, ModifierProduct.modifier_id == Modifier.id
    ).where(
        ModifierProduct.product_id == product_id,
        Modifier.is_active == 1
    ).order_by(Modifier.id.asc())
    return db.execute(j).scalars().all()
