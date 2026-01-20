# backend/crud/inventory_crud.py
"""
CRUD operations for inventory management
Phase 1 - Inventory tracking and restocking
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from backend.models.inventory import (
    Inventory, IngredientRaw, Unit, Category
)
from backend.schemas.inventory_schemas import (
    InventoryCreate, InventoryUpdate
)


def create_inventory(
    db: Session,
    payload: InventoryCreate
) -> Inventory:
    """
    Create a new inventory record

    Validation:
    - ingredient must exist
    - unit must exist
    - quantities must be >= 0
    """
    # Validate ingredient exists
    ingredient = db.query(IngredientRaw).filter(
        IngredientRaw.name == payload.ingredient_name
    ).first()
    if not ingredient:
        raise ValueError(f"Ingredient '{payload.ingredient_name}' does not exist")

    # Validate unit exists
    unit = db.query(Unit).filter(Unit.name == payload.unit_name).first()
    if not unit:
        raise ValueError(f"Unit '{payload.unit_name}' does not exist")

    # Validate quantities
    if payload.standard_qty is not None and payload.standard_qty < 0:
        raise ValueError("Standard quantity cannot be negative")
    if payload.actual_qty is not None and payload.actual_qty < 0:
        raise ValueError("Actual quantity cannot be negative")

    # Check restock_needed based on threshold
    restock_needed = 0
    if ingredient.threshold is not None and payload.actual_qty is not None:
        if payload.actual_qty < ingredient.threshold:
            restock_needed = 1

    # Create inventory record
    inventory = Inventory(
        ingredient_id=ingredient.id,
        unit_id=unit.id,
        standard_qty=payload.standard_qty,
        actual_qty=payload.actual_qty,
        location=payload.location,
        update_time=datetime.now(),
        restock_needed=restock_needed
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


def list_inventory(
    db: Session,
    group_by: Optional[str] = None,
    sort_by: Optional[str] = None,
    store_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    List inventory with optional grouping and sorting

    Args:
        group_by: 'location' or 'restock_needed'
        sort_by: 'actual_qty', 'standard_qty', or 'update_time'
        store_id: Filter by store (future feature)
        skip/limit: Pagination

    Returns:
        List of inventory records with denormalized data
    """
    query = db.query(
        Inventory.id,
        Inventory.ingredient_id,
        Inventory.standard_qty,
        Inventory.actual_qty,
        Inventory.location,
        Inventory.update_time,
        Inventory.restock_needed,
        IngredientRaw.name.label("ingredient_name"),
        IngredientRaw.brand,
        Category.name.label("category_name"),
        Unit.abbreviation.label("unit_abbreviation")
    ).join(
        IngredientRaw,
        Inventory.ingredient_id == IngredientRaw.id
    ).join(
        Category,
        IngredientRaw.category_id == Category.id
    ).join(
        Unit,
        Inventory.unit_id == Unit.id
    )

    # Apply sorting
    if sort_by == "actual_qty":
        query = query.order_by(Inventory.actual_qty.desc())
    elif sort_by == "standard_qty":
        query = query.order_by(Inventory.standard_qty.desc())
    elif sort_by == "update_time":
        query = query.order_by(Inventory.update_time.desc())
    else:
        # Default: sort by ingredient name
        query = query.order_by(IngredientRaw.name)

    # Apply pagination
    inventory_records = query.offset(skip).limit(limit).all()

    result = []
    for inv in inventory_records:
        # Convert datetime to ISO string
        update_time_str = inv.update_time.isoformat() if inv.update_time else None

        result.append({
            "inventory_id": inv.id,
            "ingredient_id": inv.ingredient_id,
            "ingredient_name": inv.ingredient_name,
            "category_name": inv.category_name,
            "brand": inv.brand,
            "standard_qty": inv.standard_qty,
            "actual_qty": inv.actual_qty,
            "unit_abbreviation": inv.unit_abbreviation,
            "location": inv.location,
            "update_time": update_time_str,
            "restock_needed": bool(inv.restock_needed)
        })

    # Apply grouping if requested (for frontend convenience)
    if group_by == "location":
        # Sort by location
        result.sort(key=lambda x: x["location"])
    elif group_by == "restock_needed":
        # Sort by restock_needed (True first)
        result.sort(key=lambda x: (not x["restock_needed"], x["ingredient_name"]))

    return result


def get_inventory_by_id(
    db: Session,
    inventory_id: int
) -> Optional[Inventory]:
    """Get inventory record by ID"""
    return db.query(Inventory).filter(Inventory.id == inventory_id).first()


def update_inventory(
    db: Session,
    inventory_id: int,
    payload: InventoryUpdate
) -> Optional[Inventory]:
    """
    Update inventory actual quantity

    Logic:
    - Update actual_qty and update_time
    - Recalculate restock_needed based on ingredient threshold
    """
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        return None

    # Validate quantity
    if payload.actual_qty < 0:
        raise ValueError("Actual quantity cannot be negative")

    # Update actual_qty
    inventory.actual_qty = payload.actual_qty
    inventory.update_time = datetime.now()

    # Get ingredient to check threshold
    ingredient = db.query(IngredientRaw).filter(
        IngredientRaw.id == inventory.ingredient_id
    ).first()

    # Recalculate restock_needed
    if ingredient and ingredient.threshold is not None:
        if payload.actual_qty < ingredient.threshold:
            inventory.restock_needed = 1
        else:
            inventory.restock_needed = 0
    else:
        inventory.restock_needed = 0

    db.commit()
    db.refresh(inventory)
    return inventory


def delete_inventory(
    db: Session,
    inventory_id: int
) -> bool:
    """Delete an inventory record"""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        return False

    db.delete(inventory)
    db.commit()
    return True
