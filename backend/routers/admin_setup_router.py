# backend/routers/admin_setup_router.py
"""
Admin Setup Router - System Configuration (Phase 0)
For Admin/Operation Manager to configure dictionary data (categories, units, allergens)
Used infrequently for initial setup and maintenance
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.inventory_schemas import (
    CategoryCreate, CategoryOut, CategoryUpdate,
    UnitCreate, UnitOut, UnitUpdate, UnitBatchResponse,
    AllergenCreate, AllergenOut, AllergenUpdate
)
from backend.crud import admin_setup_crud


router = APIRouter(prefix="/admin/setup", tags=["Admin Setup"])


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ====== Category Endpoints ======

@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_or_update_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    功能 1.1: 创建或更新分类（Category）

    - 接收: name (Fruit/Veggie...), tag (可选), unit_names (该分类允许的单位名称列表)
    - 如果是新分类: 插入 categories 并写入 category_units
    - 如果是已有分类: 更新 tag 和对应的 category_units
    - 校验:
        - 分类名唯一（如果已存在则更新）
        - unit_names 必须存在于 units 表中（按名称自动查找并关联 ID）

    Request Body:
    ```json
    {
        "name": "Fruit",
        "tag": "Fresh fruits",
        "unit_names": ["kilogram", "pound", "gram"]
    }
    ```
    """
    try:
        category = admin_setup_crud.create_category(db, payload)

        # Fetch units for response
        units = admin_setup_crud.get_category_units(db, category.id)

        return CategoryOut(
            id=category.id,
            name=category.name,
            tag=category.tag,
            units=units
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create/update category: {str(e)}"
        )
@router.get("/categories", response_model=List[CategoryOut])
def list_categories(
    name: Optional[str] = Query(None, description="Filter by category name (fuzzy search)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    功能 1.2: 获取分类列表

    - 可选查询条件: 无或按 name 模糊搜索
    - 返回每个分类及其支持的单位（unit 列表）
    - 主要用于: 前端下拉（创建原料时选 type）

    Query Parameters:
    - name: Optional filter by name (e.g., "Fruit")
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    categories_data = admin_setup_crud.list_categories(
        db,
        name_filter=name,
        skip=skip,
        limit=limit
    )

    # Convert to response model
    result = []
    for cat_data in categories_data:
        result.append(CategoryOut(
            id=cat_data["id"],
            name=cat_data["name"],
            tag=cat_data["tag"],
            units=cat_data["units"]
        ))

    return result


@router.get("/categories/{category_name}", response_model=CategoryOut)
def get_category(
    category_name: str,
    db: Session = Depends(get_db)
):
    """Get a specific category by name with its allowed units"""
    category = admin_setup_crud.get_category_by_name(db, category_name)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with name '{category_name}' not found"
        )

    units = admin_setup_crud.get_category_units(db, category.id)

    return CategoryOut(
        id=category.id,
        name=category.name,
        tag=category.tag,
        units=units
    )


@router.put("/categories/{category_name}", response_model=CategoryOut)
def update_category(
    category_name: str,
    payload: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing category by name"""
    try:
        category = admin_setup_crud.update_category_by_name(db, category_name, payload)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with name '{category_name}' not found"
            )

        units = admin_setup_crud.get_category_units(db, category.id)

        return CategoryOut(
            id=category.id,
            name=category.name,
            tag=category.tag,
            units=units
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/categories/{category_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_name: str,
    db: Session = Depends(get_db)
):
    """Delete a category and its unit associations by name"""
    success = admin_setup_crud.delete_category_by_name(db, category_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with name '{category_name}' not found"
        )


# ====== Unit Endpoints (Future Use) ======

@router.post("/units", response_model=UnitBatchResponse, status_code=status.HTTP_201_CREATED)
def create_units(
    payload: List[UnitCreate],
    db: Session = Depends(get_db)
):
    """
    Create one or multiple units of measurement in batch.

    Units that already exist will be skipped automatically without causing an error.
    The response includes both successfully created units and skipped units.

    Request Body:
    ```json
    [
        {"name": "kilogram", "abbreviation": "kg"},
        {"name": "pound", "abbreviation": "lb"},
        {"name": "gram", "abbreviation": "g"}
    ]
    ```

    Response:
    ```json
    {
        "created": [
            {"id": 1, "name": "kilogram", "abbreviation": "kg"},
            {"id": 2, "name": "pound", "abbreviation": "lb"}
        ],
        "skipped": [
            {"name": "gram", "abbreviation": "g", "reason": "already exists"}
        ]
    }
    ```
    """
    result = admin_setup_crud.create_units_batch(db, payload)
    return UnitBatchResponse(
        created=result["created"],
        skipped=result["skipped"]
    )
@router.get("/units", response_model=List[UnitOut])
def list_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all units of measurement"""
    units = admin_setup_crud.list_units(db, skip=skip, limit=limit)
    return units



@router.delete("/units/{unit_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_name: str,
    db: Session = Depends(get_db)
):
    """Delete a unit by name"""
    success = admin_setup_crud.delete_unit_by_name(db, unit_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unit with name '{unit_name}' not found"
        )


# ====== Allergen Endpoints (Future Use) ======

@router.post("/allergens", response_model=AllergenOut, status_code=status.HTTP_201_CREATED)
def create_allergen(
    payload: AllergenCreate,
    db: Session = Depends(get_db)
):
    """Create a new allergen"""
    # Check if allergen already exists
    existing = admin_setup_crud.get_allergen_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allergen with name '{payload.name}' already exists"
        )

    allergen = admin_setup_crud.create_allergen(db, payload)
    return allergen


@router.get("/allergens", response_model=List[AllergenOut])
def list_allergens(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all allergens"""
    allergens = admin_setup_crud.list_allergens(db, skip=skip, limit=limit)
    return allergens