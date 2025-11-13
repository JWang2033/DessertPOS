# backend/crud/admin_catalog_crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from backend.models.catalog import (
    Product, ProductType, Modifier, ModifierProduct
)
from backend.schemas.catalog_schemas import (
    ProductCreate, ProductUpdate, ModifierCreate, ModifierUpdate, ProductTypeCreate
)

# -------- ProductType --------
def create_category(db: Session, payload: ProductTypeCreate) -> ProductType:
    obj = ProductType(name=payload.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_category(db: Session, type_id: int) -> int:
    # 简单删除（注意：若有产品引用需要你在 DB 层处理约束/联动）
    q = db.query(ProductType).filter(ProductType.id == type_id)
    if not q.first():
        return 0
    q.delete()
    db.commit()
    return 1

# -------- Product --------
def create_product(db: Session, payload: ProductCreate) -> Product:
    obj = Product(
        name=payload.name,
        price=payload.price,
        type_id=payload.type_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Optional[Product]:
    obj = db.query(Product).filter(Product.id == product_id).first()
    if not obj:
        return None
    if payload.name is not None:
        obj.name = payload.name
    if payload.price is not None:
        obj.price = payload.price
    if payload.type_id is not None:
        obj.type_id = payload.type_id
    db.commit()
    db.refresh(obj)
    return obj

def delete_product(db: Session, product_id: int) -> int:
    q = db.query(Product).filter(Product.id == product_id)
    if not q.first():
        return 0
    # 同步清理关联的 modifier_product
    db.query(ModifierProduct).filter(ModifierProduct.product_id == product_id).delete()
    q.delete()
    db.commit()
    return 1

# -------- Modifier --------
def create_modifier(db: Session, payload: ModifierCreate) -> Modifier:
    obj = Modifier(
        name=payload.name,
        type=payload.type,
        price=payload.price,
        is_active=payload.is_active,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_modifier(db: Session, modifier_id: int, payload: ModifierUpdate) -> Optional[Modifier]:
    obj = db.query(Modifier).filter(Modifier.id == modifier_id).first()
    if not obj:
        return None
    if payload.name is not None:
        obj.name = payload.name
    if payload.type is not None:
        obj.type = payload.type
    if payload.price is not None:
        obj.price = payload.price
    if payload.is_active is not None:
        obj.is_active = payload.is_active
    db.commit()
    db.refresh(obj)
    return obj

def delete_modifier(db: Session, modifier_id: int) -> int:
    q = db.query(Modifier).filter(Modifier.id == modifier_id)
    if not q.first():
        return 0
    # 同步清理关联
    db.query(ModifierProduct).filter(ModifierProduct.modifier_id == modifier_id).delete()
    q.delete()
    db.commit()
    return 1

# -------- Relations: product <-> modifier --------
def attach_modifier(db: Session, product_id: int, modifier_id: int) -> bool:
    exists = db.query(ModifierProduct).filter(
        ModifierProduct.product_id == product_id,
        ModifierProduct.modifier_id == modifier_id
    ).first()
    if exists:
        return False
    db.add(ModifierProduct(product_id=product_id, modifier_id=modifier_id))
    db.commit()
    return True

def detach_modifier(db: Session, product_id: int, modifier_id: int) -> int:
    q = db.query(ModifierProduct).filter(
        ModifierProduct.product_id == product_id,
        ModifierProduct.modifier_id == modifier_id
    )
    count = q.delete()
    db.commit()
    return count
