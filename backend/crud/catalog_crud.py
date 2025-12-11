# backend/crud/catalog_crud.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from backend.models.catalog import (
    Product, ProductType, Modifier, ModifierProduct
)
from backend.models.order import ProductAllergen

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


def list_products_filtered_by_allergens(
    db: Session,
    exclude_allergens: List[str],
    category_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Product]:
    """根据过敏原筛选产品列表"""
    # 规范化过敏原名称（转小写）
    exclude_allergens = [a.lower() for a in exclude_allergens]

    # 获取包含指定过敏原的产品ID
    if exclude_allergens:
        excluded_product_ids = db.execute(
            select(ProductAllergen.product_id)
            .where(ProductAllergen.allergen.in_(exclude_allergens))
            .distinct()
        ).scalars().all()
    else:
        excluded_product_ids = []

    # 查询产品，排除包含过敏原的产品
    conditions = []
    if excluded_product_ids:
        conditions.append(Product.id.notin_(excluded_product_ids))
    if category_id:
        conditions.append(Product.type_id == category_id)

    stmt = select(Product).where(and_(*conditions) if conditions else True)\
        .order_by(Product.id.asc())\
        .limit(limit).offset(offset)

    return db.execute(stmt).scalars().all()


def get_product_allergens(db: Session, product_id: int) -> List[str]:
    """获取产品的过敏原列表"""
    allergens = db.execute(
        select(ProductAllergen.allergen).where(ProductAllergen.product_id == product_id)
    ).scalars().all()
    return list(allergens)
