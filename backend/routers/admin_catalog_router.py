# backend/routers/admin_catalog_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.utils.auth_dependencies import require_roles
from backend.schemas.catalog_schemas import (
    ProductCreate, ProductUpdate, ProductOut,
    ModifierCreate, ModifierUpdate, ModifierOut,
    ProductTypeCreate, ProductTypeOut,
    AttachModifierRequest
)
from backend.crud import admin_catalog_crud, catalog_crud

# 说明：
# 这个 router 专门用于「管理端」的商品目录配置（RBAC 保护）
# 统一前缀：/admin/catalog/...
router = APIRouter(prefix="/admin/catalog", tags=["AdminCatalog"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- 分类 ----------

# 接口说明：
# 功能：创建商品分类（ProductType）
# URL：POST /admin/catalog/category
# 请求体格式：JSON，对应 ProductTypeCreate，例如：
#   {
#     "name": "Milk Tea"
#   }
# 权限：需要 Header 携带员工端 Token，
#   Authorization: Bearer <staff_token>
#   且当前 staff 角色需为 owner 或 manager
@router.post("/category", response_model=ProductTypeOut)
def create_category(
    payload: ProductTypeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    return admin_catalog_crud.create_category(db, payload)


# 接口说明：
# 功能：删除商品分类
# URL：DELETE /admin/catalog/category/{type_id}
# 路径参数：
#   type_id: 分类 ID（整数）
# 请求体：无（空 Body）
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.delete("/category/{type_id}")
def delete_category(
    type_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    ok = admin_catalog_crud.delete_category(db, type_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found or not deleted")
    return {"deleted": ok}

# ---------- 产品 ----------

# 接口说明：
# 功能：创建产品（商品）
# URL：POST /admin/catalog/product
# 请求体格式：JSON，对应 ProductCreate，例如：
#   {
#     "name": "Brown Sugar Milk Tea",
#     "price": 5.50,
#     "type_id": 1
#   }
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.post("/product", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    return admin_catalog_crud.create_product(db, payload)


# 接口说明：
# 功能：更新产品信息（部分字段）
# URL：PATCH /admin/catalog/product/{product_id}
# 路径参数：
#   product_id: 产品 ID
# 请求体格式：JSON，对应 ProductUpdate，例如：
#   {
#     "name": "New Name",
#     "price": 6.00
#   }
#   （可只传需要更新的字段）
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.patch("/product/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    obj = admin_catalog_crud.update_product(db, product_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


# 接口说明：
# 功能：删除产品
# URL：DELETE /admin/catalog/product/{product_id}
# 路径参数：
#   product_id: 产品 ID
# 请求体：无（空 Body）
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.delete("/product/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    ok = admin_catalog_crud.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found or not deleted")
    return {"deleted": ok}

# ---------- 修饰项（Modifier） ----------

# 接口说明：
# 功能：创建修饰项（Modifier），如「加珍珠」「少冰」「无糖」等
# URL：POST /admin/catalog/modifier
# 请求体格式：JSON，对应 ModifierCreate，例如：
#   {
#     "name": "Add Pearl",
#     "type": "topping",
#     "price": 0.50,
#     "is_active": true
#   }
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.post("/modifier", response_model=ModifierOut)
def create_modifier(
    payload: ModifierCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    return admin_catalog_crud.create_modifier(db, payload)


# 接口说明：
# 功能：更新修饰项信息
# URL：PATCH /admin/catalog/modifier/{modifier_id}
# 路径参数：
#   modifier_id: 修饰项 ID
# 请求体格式：JSON，对应 ModifierUpdate，例如：
#   {
#     "name": "Less Ice",
#     "price": 0.00,
#     "is_active": true
#   }
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.patch("/modifier/{modifier_id}", response_model=ModifierOut)
def update_modifier(
    modifier_id: int,
    payload: ModifierUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    obj = admin_catalog_crud.update_modifier(db, modifier_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Modifier not found")
    return obj


# 接口说明：
# 功能：删除修饰项
# URL：DELETE /admin/catalog/modifier/{modifier_id}
# 路径参数：
#   modifier_id: 修饰项 ID
# 请求体：无（空 Body）
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.delete("/modifier/{modifier_id}")
def delete_modifier(
    modifier_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    ok = admin_catalog_crud.delete_modifier(db, modifier_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Modifier not found or not deleted")
    return {"deleted": ok}

# ---------- 关联：产品 <-> 修饰项 ----------

# 接口说明：
# 功能：给某个产品挂载一个修饰项（在中间表 modifier_product 里插入关联）
# URL：POST /admin/catalog/product/{product_id}/modifiers
# 路径参数：
#   product_id: 产品 ID
# 请求体格式：JSON，对应 AttachModifierRequest，例如：
#   {
#     "modifier_id": 3
#   }
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.post("/product/{product_id}/modifiers")
def attach_modifier(
    product_id: int,
    payload: AttachModifierRequest,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    created = admin_catalog_crud.attach_modifier(db, product_id, payload.modifier_id)
    return {"attached": created}


# 接口说明：
# 功能：把某个修饰项从产品上解绑（删除关联记录）
# URL：DELETE /admin/catalog/product/{product_id}/modifiers/{modifier_id}
# 路径参数：
#   product_id: 产品 ID
#   modifier_id: 修饰项 ID
# 请求体：无（空 Body）
# 权限：需要 Authorization: Bearer <staff_token>，角色 owner 或 manager
@router.delete("/product/{product_id}/modifiers/{modifier_id}")
def detach_modifier(
    product_id: int,
    modifier_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["owner", "manager"])),
):
    deleted = admin_catalog_crud.detach_modifier(db, product_id, modifier_id)
    return {"detached": bool(deleted)}
