# backend/routers/product_router.py
"""
Product Router - Semi-Finished Products (Prepped Items) Management
For creating and managing semi-finished products in the inventory system
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.inventory_schemas import (
    SemiFinishedProductCreate, SemiFinishedProductOut,
    SemiFinishedProductUpdate, SemiFinishedProductListOut
)
from backend.crud import product_crud


router = APIRouter(prefix="/prepped-items", tags=["Semi-Finished Products"])


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ====== Semi-Finished Product Endpoints ======

@router.post("", response_model=SemiFinishedProductOut, status_code=status.HTTP_201_CREATED)
def create_prepped_item(
    payload: SemiFinishedProductCreate,
    db: Session = Depends(get_db)
):
    """
    功能 3.1: 创建半成品 (Create Semi-Finished Product / Prepped Item)

    Body:
    - name: Unique name for the semi-finished product
    - prep_time_hours: Preparation time in hours (must be > 0)
    - ingredients: List of ingredients with:
      - ingredient_name: Name of the ingredient
      - unit_name: Unit name (must be allowed for the ingredient's category)
      - quantity: Amount (must be > 0)

    Validation:
    - name must be unique in semi_finished_products table
    - ingredient_name must exist in ingredients table
    - unit_name must exist and be allowed for the ingredient's category
    - quantity must be > 0

    Writes to:
    - semi_finished_products (header)
    - semi_finished_product_ingredients (details)

    Request Body:
    ```json
    {
        "name": "Chocolate Ganache",
        "prep_time_hours": 2.5,
        "ingredients": [
            {
                "ingredient_name": "Dark Chocolate",
                "unit_name": "gram",
                "quantity": 500
            },
            {
                "ingredient_name": "Heavy Cream",
                "unit_name": "milliliter",
                "quantity": 250
            }
        ]
    }
    ```
    """
    try:
        # Check if name already exists
        existing = product_crud.get_semi_finished_product_by_name(db, payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Semi-finished product with name '{payload.name}' already exists"
            )

        product = product_crud.create_semi_finished_product(db, payload)

        # Get ingredient details for response
        ingredients = product_crud.get_semi_finished_product_ingredients(db, product.id)

        return SemiFinishedProductOut(
            id=product.id,
            name=product.name,
            prep_time_hours=product.prep_time_hours,
            ingredients=ingredients
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create semi-finished product: {str(e)}"
        )


@router.get("", response_model=List[SemiFinishedProductListOut])
def list_prepped_items(
    name: Optional[str] = Query(None, description="Filter by name (fuzzy search)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    功能 3.2: 获取半成品列表 (Get Semi-Finished Products List)

    Query parameters:
    - name: Fuzzy search by name
    - skip/limit: Pagination

    Returns:
    - id, name, prep_time_hours, ingredient_count

    Used for:
    - Recipe management page listing
    - Referencing semi-finished products in other modules (future)

    Example: GET /prepped-items?name=ganache&skip=0&limit=10
    """
    products_data = product_crud.list_semi_finished_products(
        db,
        name_filter=name,
        skip=skip,
        limit=limit
    )

    return [SemiFinishedProductListOut(**product) for product in products_data]


@router.get("/{product_name}", response_model=SemiFinishedProductOut)
def get_prepped_item(
    product_name: str,
    db: Session = Depends(get_db)
):
    """
    功能 3.3: 获取半成品详情 (Get Semi-Finished Product Details)

    Returns:
    - Header info: id, name, prep_time_hours
    - All ingredient details: ingredient_id, ingredient_name, quantity, unit_abbreviation

    Used for:
    - Editing recipes
    - Viewing recipe details
    """
    product = product_crud.get_semi_finished_product_by_name(db, product_name)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Semi-finished product with name '{product_name}' not found"
        )

    # Get ingredient details
    ingredients = product_crud.get_semi_finished_product_ingredients(db, product.id)

    return SemiFinishedProductOut(
        id=product.id,
        name=product.name,
        prep_time_hours=product.prep_time_hours,
        ingredients=ingredients
    )


@router.put("/{product_name}", response_model=SemiFinishedProductOut)
def update_prepped_item(
    product_name: str,
    payload: SemiFinishedProductUpdate,
    db: Session = Depends(get_db)
):
    """
    功能 3.4: 更新半成品 (Update Semi-Finished Product)

    Supports updating:
    - name
    - prep_time_hours
    - ingredients: Replaces the entire ingredient list

    The ingredient details table (semi_finished_product_ingredients) will be
    completely replaced with the new list.

    Request Body:
    ```json
    {
        "name": "Premium Chocolate Ganache",
        "prep_time_hours": 3.0,
        "ingredients": [
            {
                "ingredient_name": "Dark Chocolate",
                "unit_name": "gram",
                "quantity": 600
            },
            {
                "ingredient_name": "Heavy Cream",
                "unit_name": "milliliter",
                "quantity": 300
            },
            {
                "ingredient_name": "Butter",
                "unit_name": "gram",
                "quantity": 50
            }
        ]
    }
    ```
    """
    try:
        product = product_crud.update_semi_finished_product_by_name(
            db, product_name, payload
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Semi-finished product with name '{product_name}' not found"
            )

        # Get updated ingredient details
        ingredients = product_crud.get_semi_finished_product_ingredients(db, product.id)

        return SemiFinishedProductOut(
            id=product.id,
            name=product.name,
            prep_time_hours=product.prep_time_hours,
            ingredients=ingredients
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{product_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prepped_item(
    product_name: str,
    db: Session = Depends(get_db)
):
    """
    Delete a semi-finished product and its ingredient associations by name

    Note: This will fail if the product is referenced by:
    - Recipes
    - Production records (future)
    """
    success = product_crud.delete_semi_finished_product_by_name(db, product_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Semi-finished product with name '{product_name}' not found"
        )
