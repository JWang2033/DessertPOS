# backend/routers/inventory_router.py
"""
Inventory Router - Inventory Management
For tracking ingredient stock levels and restocking
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas.inventory_schemas import (
    InventoryCreate, InventoryOut, InventoryUpdate
)
from backend.crud import inventory_crud


router = APIRouter(prefix="/inventory", tags=["Inventory"])


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ====== Inventory Endpoints ======

@router.get("", response_model=List[InventoryOut])
def get_inventory_list(
    group_by: Optional[str] = Query(None, description="Group by: 'location' or 'restock_needed'"),
    sort_by: Optional[str] = Query(None, description="Sort by: 'actual_qty', 'standard_qty', or 'update_time'"),
    store_id: Optional[str] = Query(None, description="Filter by store ID (future feature)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    功能 5.1: 获取库存列表 (Get Inventory List / Inventory View)

    面向：Store Manager, Warehouse Staff
    用途：View current inventory levels and identify items needing restock

    Query Parameters:
    - group_by: Group results by 'location' or 'restock_needed'
    - sort_by: Sort by 'actual_qty', 'standard_qty', or 'update_time'
    - store_id: Filter by store (future multi-store support)
    - skip/limit: Pagination

    Returns for each inventory record:
    - inventory_id: Unique identifier
    - ingredient_id, ingredient_name: Ingredient details
    - category_name: Category of ingredient
    - brand: Brand name if applicable
    - standard_qty: Target quantity to maintain
    - actual_qty: Current quantity in stock
    - unit_abbreviation: Unit measurement
    - location: Storage location (e.g., "Freezer A", "Dry Storage")
    - update_time: Last update timestamp (ISO format)
    - restock_needed: Boolean flag (true if actual_qty < threshold)

    Frontend Usage:
    - Group by location to organize warehouse layout
    - Filter by restock_needed=true to show items requiring reorder
    - Sort by actual_qty to prioritize low stock items

    Example Queries:
    - GET /inventory
      Returns all inventory records

    - GET /inventory?group_by=location
      Returns inventory grouped by storage location

    - GET /inventory?group_by=restock_needed
      Returns inventory with low stock items first

    - GET /inventory?sort_by=actual_qty
      Returns inventory sorted by quantity (lowest first)

    - GET /inventory?sort_by=update_time
      Returns inventory sorted by most recently updated

    Response Example:
    ```json
    [
        {
            "inventory_id": 1,
            "ingredient_id": 1,
            "ingredient_name": "Strawberry",
            "category_name": "Fruit",
            "brand": "Fresh Farms",
            "standard_qty": "50.00",
            "actual_qty": "15.00",
            "unit_abbreviation": "kg",
            "location": "Cold Storage A",
            "update_time": "2026-01-20T10:30:00",
            "restock_needed": true
        },
        {
            "inventory_id": 2,
            "ingredient_id": 2,
            "ingredient_name": "Blueberry",
            "category_name": "Fruit",
            "brand": null,
            "standard_qty": "30.00",
            "actual_qty": "28.00",
            "unit_abbreviation": "kg",
            "location": "Cold Storage A",
            "update_time": "2026-01-20T09:15:00",
            "restock_needed": false
        },
        {
            "inventory_id": 3,
            "ingredient_name": "Heavy Cream",
            "category_name": "Dairy",
            "brand": "Premium Dairy Co.",
            "standard_qty": "40.00",
            "actual_qty": "8.00",
            "unit_abbreviation": "L",
            "location": "Refrigerator B",
            "update_time": "2026-01-19T16:45:00",
            "restock_needed": true
        }
    ]
    ```
    """
    inventory_list = inventory_crud.list_inventory(
        db,
        group_by=group_by,
        sort_by=sort_by,
        store_id=store_id,
        skip=skip,
        limit=limit
    )

    return [InventoryOut(**item) for item in inventory_list]


@router.put("/{inventory_id}", response_model=InventoryOut)
def update_inventory_quantity(
    inventory_id: int,
    payload: InventoryUpdate,
    db: Session = Depends(get_db)
):
    """
    功能 5.2: 更新某条库存 (Update Inventory Actual Quantity)

    面向：Store Manager, Warehouse Staff
    用途：Update actual stock quantity after receiving, usage, or physical count

    URL Parameter:
    - inventory_id: Unique inventory record ID

    Body:
    - actual_qty: New actual quantity (must be >= 0)

    Internal Logic:
    1. Update actual_qty in inventory table
    2. Set update_time to current timestamp
    3. Recalculate restock_needed:
       - If ingredient has threshold AND actual_qty < threshold: restock_needed = 1
       - Otherwise: restock_needed = 0

    Use Cases:
    - After receiving new stock from purchase order
    - After daily/weekly physical inventory count
    - After production usage (deduct ingredients used)
    - Manual adjustments for waste or damage

    Request Body Example:
    ```json
    {
        "actual_qty": 45.5
    }
    ```

    Response Example:
    ```json
    {
        "inventory_id": 1,
        "ingredient_id": 1,
        "ingredient_name": "Strawberry",
        "category_name": "Fruit",
        "brand": "Fresh Farms",
        "standard_qty": "50.00",
        "actual_qty": "45.50",
        "unit_abbreviation": "kg",
        "location": "Cold Storage A",
        "update_time": "2026-01-20T14:22:35",
        "restock_needed": false
    }
    ```

    Error Responses:
    - 400: Invalid quantity (negative number)
    - 404: Inventory record not found
    """
    try:
        inventory = inventory_crud.update_inventory(db, inventory_id, payload)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory record with ID {inventory_id} not found"
            )

        # Get denormalized data for response
        inventory_list = inventory_crud.list_inventory(db, skip=0, limit=1)
        # Find the updated record
        for item in inventory_list:
            if item["inventory_id"] == inventory_id:
                return InventoryOut(**item)

        # Fallback: query again specifically
        inventory_data = inventory_crud.list_inventory(db)
        for item in inventory_data:
            if item["inventory_id"] == inventory_id:
                return InventoryOut(**item)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated inventory record"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_inventory_record(
    payload: InventoryCreate,
    db: Session = Depends(get_db)
):
    """
    功能 5.3: 初始化或创建库存记录 (Create/Initialize Inventory Record)

    面向：Store Manager, System Admin
    用途：Create initial inventory records for new ingredients or locations

    Body:
    - ingredient_name: Name of the ingredient
    - unit_name: Unit of measurement
    - standard_qty: Target quantity to maintain (optional)
    - actual_qty: Current quantity (optional, defaults to 0)
    - location: Storage location

    Use Cases:
    - Setting up inventory for new store opening
    - Adding new ingredient to existing store
    - Creating separate inventory records for same ingredient in different locations
    - Initial system setup

    Validation:
    - ingredient_name must exist in ingredients table
    - unit_name must exist in units table
    - quantities must be >= 0

    Internal Logic:
    - Automatically calculates restock_needed based on ingredient threshold
    - Sets update_time to current timestamp

    Request Body Example:
    ```json
    {
        "ingredient_name": "Strawberry",
        "unit_name": "kilogram",
        "standard_qty": 50.0,
        "actual_qty": 30.0,
        "location": "Cold Storage A"
    }
    ```

    Response Example:
    ```json
    {
        "inventory_id": 4,
        "ingredient_id": 1,
        "ingredient_name": "Strawberry",
        "category_name": "Fruit",
        "brand": "Fresh Farms",
        "standard_qty": "50.00",
        "actual_qty": "30.00",
        "unit_abbreviation": "kg",
        "location": "Cold Storage A",
        "update_time": "2026-01-20T15:00:00",
        "restock_needed": false
    }
    ```

    Error Responses:
    - 400: Invalid ingredient or unit name, or negative quantities
    """
    try:
        inventory = inventory_crud.create_inventory(db, payload)

        # Get denormalized data for response
        inventory_data = inventory_crud.list_inventory(db)
        for item in inventory_data:
            if item["inventory_id"] == inventory.id:
                return InventoryOut(**item)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created inventory record"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
