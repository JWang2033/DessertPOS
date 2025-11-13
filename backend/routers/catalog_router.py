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

@router.get("/categories", response_model=List[ProductTypeOut])
def list_categories(db: Session = Depends(get_db)):
    return catalog_crud.list_categories(db)

@router.get("/products", response_model=List[ProductOut])
def list_products(
    categoryId: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items = catalog_crud.list_products(db, category_id=categoryId, limit=limit, offset=offset)
    return items

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
