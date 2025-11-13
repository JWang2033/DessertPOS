# backend/routers/catalog_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.catalog_schemas import (
    ProductQuery, ProductOut, ProductDetail, ProductTypeOut, ModifierOut
)
from backend.crud import catalog_crud

router = APIRouter(prefix="/catalog", tags=["Catalog"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# 获取所有分类
# ---------------------------------------------------------
# 接口说明：
# 功能：获取所有产品分类（如：奶茶类、热饮、甜品等），用于顾客端展示分类导航。
# URL：GET /catalog/categories
# 路径参数：无
# 请求体格式：无（GET 无 Body）
# 权限：不需要 Authorization（公开接口）
@router.get("/categories", response_model=List[ProductTypeOut])
def list_categories(db: Session = Depends(get_db)):
    return catalog_crud.list_categories(db)

# ---------------------------------------------------------
# 获取产品列表（支持分类筛选 + 分页）
# ---------------------------------------------------------
# 接口说明：
# 功能：按分类获取商品列表，或获取全部商品。用于顾客端展示商品页。
# URL：GET /catalog/products
# 查询参数（Query Params）：
#   categoryId：可选，分类 ID（数字）
#   limit：可选，每页数量（默认 100）
#   offset：可选，偏移量（默认 0）
# 请求体格式：无（使用 Query 参数）
# 权限：不需要 Authorization（公开接口）
@router.get("/products", response_model=List[ProductOut])
def list_products(
    categoryId: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items = catalog_crud.list_products(db, category_id=categoryId, limit=limit, offset=offset)
    return items

# ---------------------------------------------------------
# 获取产品详情（含 modifiers）
# ---------------------------------------------------------
# 接口说明：
# 功能：获取某个产品的完整详情，包括关联的所有 modifier（如加料、甜度等）。
# URL：GET /catalog/products/{product_id}
# 路径参数：
#   product_id：产品 ID
# 请求体格式：无
# 权限：不需要 Authorization（公开接口）
@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = catalog_crud.get_product(db, product_id)
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    modifiers = catalog_crud.get_product_modifiers(db, product_id)
    return {
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "type_id": p.type_id,
        "modifiers": modifiers
    }
