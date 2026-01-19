# backend/routers/ingredient_router.py
"""
Ingredient Router - Ingredient Management
For creating and managing raw ingredients in the inventory system
"""
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.inventory_schemas import (
    IngredientCreate, IngredientOut, IngredientUpdate,
    IngredientListOut, IngredientBatchResponse, AllergenOut
)
from backend.crud import ingredient_crud
from backend.models.inventory import Category


router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_category_name(db: Session, category_id: int) -> str:
    """Helper function to get category name by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    return category.name if category else "Unknown"


# ====== Ingredient Endpoints ======

@router.post("", response_model=Union[IngredientOut, IngredientBatchResponse], status_code=status.HTTP_201_CREATED)
def create_ingredients(
    payload: Union[IngredientCreate, List[IngredientCreate]],
    db: Session = Depends(get_db)
):
    """
    功能 2.1: 创建 / 批量创建原料（Ingredients）

    Supports single or batch creation:
    - Single: Pass an IngredientCreate object
    - Batch: Pass a list of IngredientCreate objects

    Validation:
    - name must be unique in ingredients table
    - category_id must exist in categories table
    - allergen_ids must exist in allergens table
    - threshold must be > 0 if provided

    Single Request Body:
    ```json
    {
        "name": "Strawberry",
        "category_name": "Fruit",
        "brand": "Fresh Farm",
        "threshold": 10.00,
        "allergen_ids": [1, 2]
    }
    ```

    Batch Request Body:
    ```json
    [
        {
            "name": "Strawberry",
            "category_name": "Fruit",
            "brand": "Fresh Farm",
            "threshold": 10.00,
            "allergen_ids": [1]
        },
        {
            "name": "Blueberry",
            "category_name": "Fruit",
            "threshold": 5.00,
            "allergen_ids": []
        }
    ]
    ```
    """
    try:
        # Check if it's a batch request (list)
        if isinstance(payload, list):
            result = ingredient_crud.create_ingredients_batch(db, payload)

            # Get allergens for created ingredients
            created_with_allergens = []
            for ingredient in result["created"]:
                allergens = ingredient_crud.get_ingredient_allergens(db, ingredient.id)
                category_name = get_category_name(db, ingredient.category_id)
                ingredient_dict = {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "category_id": ingredient.category_id,
                    "category_name": category_name,
                    "brand": ingredient.brand,
                    "threshold": ingredient.threshold,
                    "allergens": allergens
                }
                created_with_allergens.append(IngredientOut(**ingredient_dict))

            return IngredientBatchResponse(
                created=created_with_allergens,
                skipped=result["skipped"]
            )
        else:
            # Single ingredient creation
            ingredient = ingredient_crud.create_ingredient(db, payload)
            allergens = ingredient_crud.get_ingredient_allergens(db, ingredient.id)
            category_name = get_category_name(db, ingredient.category_id)

            return IngredientOut(
                id=ingredient.id,
                name=ingredient.name,
                category_id=ingredient.category_id,
                category_name=category_name,
                brand=ingredient.brand,
                threshold=ingredient.threshold,
                allergens=allergens
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ingredient(s): {str(e)}"
        )


@router.get("", response_model=List[IngredientListOut])
def list_ingredients(
    q: Optional[str] = Query(None, description="Search by name (fuzzy search for autocomplete)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    功能 2.2: 搜索 / 列出原料

    Query parameters:
    - q: Name fuzzy search (用于进货单输入时联想)
    - category_id: Filter by category
    - skip/limit: Pagination

    Returns:
    - id, name, category_name, brand, threshold, allergen_names[]

    Used for:
    - Phase 0: Selecting ingredients for semi-finished products/recipes
    - Phase 1: Searching ingredients for purchase orders

    Example: GET /ingredients?q=berry&category_id=1&skip=0&limit=10
    """
    ingredients_data = ingredient_crud.list_ingredients(
        db,
        q=q,
        category_id=category_id,
        skip=skip,
        limit=limit
    )

    return [IngredientListOut(**ingredient) for ingredient in ingredients_data]


@router.get("/{ingredient_name}", response_model=IngredientOut)
def get_ingredient(
    ingredient_name: str,
    db: Session = Depends(get_db)
):
    """
    功能 2.3: 获取单个原料详情

    Returns complete information including:
    - Basic fields (id, name, category_id, brand, threshold)
    - Associated allergens (full allergen objects)

    Used for:
    - Detail page
    - Pre-filling edit forms
    """
    ingredient = ingredient_crud.get_ingredient_by_name(db, ingredient_name)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with name '{ingredient_name}' not found"
        )

    allergens = ingredient_crud.get_ingredient_allergens(db, ingredient.id)
    category_name = get_category_name(db, ingredient.category_id)

    return IngredientOut(
        id=ingredient.id,
        name=ingredient.name,
        category_id=ingredient.category_id,
        category_name=category_name,
        brand=ingredient.brand,
        threshold=ingredient.threshold,
        allergens=allergens
    )


@router.put("/{ingredient_name}", response_model=IngredientOut)
def update_ingredient(
    ingredient_name: str,
    payload: IngredientUpdate,
    db: Session = Depends(get_db)
):
    """
    功能 2.4: 更新原料信息

    Updatable fields:
    - name
    - category_name (by category name, not ID)
    - brand
    - threshold
    - allergen_ids

    Validation is the same as creation.
    Also updates ingredient_allergens intermediate table.

    Request Body:
    ```json
    {
        "name": "Organic Strawberry",
        "category_name": "Fruit",
        "brand": "Premium Farm",
        "threshold": 15.00,
        "allergen_ids": [1, 2, 3]
    }
    ```
    """
    try:
        ingredient = ingredient_crud.update_ingredient_by_name(db, ingredient_name, payload)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with name '{ingredient_name}' not found"
            )

        allergens = ingredient_crud.get_ingredient_allergens(db, ingredient.id)
        category_name = get_category_name(db, ingredient.category_id)

        return IngredientOut(
            id=ingredient.id,
            name=ingredient.name,
            category_id=ingredient.category_id,
            category_name=category_name,
            brand=ingredient.brand,
            threshold=ingredient.threshold,
            allergens=allergens
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{ingredient_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_name: str,
    db: Session = Depends(get_db)
):
    """
    Delete an ingredient and its allergen associations by name

    Note: This will fail if the ingredient is referenced by:
    - Semi-finished products
    - Recipes
    - Inventory records
    """
    success = ingredient_crud.delete_ingredient_by_name(db, ingredient_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with name '{ingredient_name}' not found"
        )
