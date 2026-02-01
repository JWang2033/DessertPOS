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
    - unit must be allowed for ingredient's category
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

    # Validate unit is allowed for ingredient's category
    from backend.models.inventory import CategoryUnit
    allowed_units = db.query(CategoryUnit.unit_id).filter(
        CategoryUnit.category_id == ingredient.category_id
    ).all()
    allowed_unit_ids = [u[0] for u in allowed_units]

    if unit.id not in allowed_unit_ids:
        category = db.query(Category).filter(
            Category.id == ingredient.category_id
        ).first()
        raise ValueError(
            f"Unit '{unit.name}' is not allowed for ingredient '{ingredient.name}' "
            f"in category '{category.name if category else 'Unknown'}'"
        )

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
        standard_qty=payload.standard_qty if payload.standard_qty is not None else 0,
        actual_qty=payload.actual_qty if payload.actual_qty is not None else 0,
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
    Includes both regular ingredients and semi-finished products

    Args:
        group_by: 'location' or 'restock_needed'
        sort_by: 'actual_qty', 'standard_qty', or 'update_time'
        store_id: Filter by store (future feature)
        skip/limit: Pagination

    Returns:
        List of inventory records with denormalized data
    """
    from backend.models.inventory import SemiFinishedProduct, SemiProductInventory

    # Query regular ingredients inventory
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
        IngredientRaw.threshold,
        IngredientRaw.unit_id.label("threshold_unit_id"),
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

    # Query semi-finished products inventory
    semi_query = db.query(
        SemiProductInventory.id,
        SemiProductInventory.semi_product_id,
        SemiProductInventory.standard_qty,
        SemiProductInventory.actual_qty,
        SemiProductInventory.location,
        SemiProductInventory.update_time,
        SemiProductInventory.restock_needed,
        SemiFinishedProduct.name.label("product_name"),
        SemiFinishedProduct.threshold,
        SemiFinishedProduct.unit_id.label("threshold_unit_id"),
        Unit.abbreviation.label("unit_abbreviation")
    ).join(
        SemiFinishedProduct,
        SemiProductInventory.semi_product_id == SemiFinishedProduct.id
    ).join(
        Unit,
        SemiProductInventory.unit_id == Unit.id
    )

    # Apply sorting (limit to 500 per type for now, handle pagination differently)
    inventory_records = query.limit(500).all()
    semi_records = semi_query.limit(500).all()

    result = []

    # Process regular ingredients
    for inv in inventory_records:
        # Convert datetime to ISO string
        update_time_str = inv.update_time.isoformat() if inv.update_time else None

        # Get threshold unit abbreviation
        threshold_unit = None
        if inv.threshold_unit_id:
            threshold_unit_obj = db.query(Unit).filter(Unit.id == inv.threshold_unit_id).first()
            if threshold_unit_obj:
                threshold_unit = threshold_unit_obj.abbreviation

        result.append({
            "inventory_id": inv.id,
            "ingredient_id": inv.ingredient_id,
            "ingredient_name": inv.ingredient_name,
            "category_name": inv.category_name,
            "brand": inv.brand,
            "standard_qty": inv.standard_qty,
            "actual_qty": inv.actual_qty,
            "unit_abbreviation": inv.unit_abbreviation,
            "threshold": inv.threshold,
            "threshold_unit": threshold_unit,
            "location": inv.location,
            "update_time": update_time_str,
            "restock_needed": bool(inv.restock_needed),
            "item_type": "ingredient"
        })

    # Process semi-finished products
    for semi in semi_records:
        update_time_str = semi.update_time.isoformat() if semi.update_time else None

        # Get threshold unit abbreviation
        threshold_unit = None
        if semi.threshold_unit_id:
            threshold_unit_obj = db.query(Unit).filter(Unit.id == semi.threshold_unit_id).first()
            if threshold_unit_obj:
                threshold_unit = threshold_unit_obj.abbreviation

        result.append({
            "inventory_id": semi.id,
            "ingredient_id": semi.semi_product_id,
            "ingredient_name": semi.product_name,
            "category_name": "半成品",
            "brand": None,
            "standard_qty": semi.standard_qty,
            "actual_qty": semi.actual_qty,
            "unit_abbreviation": semi.unit_abbreviation,
            "threshold": semi.threshold,
            "threshold_unit": threshold_unit,
            "location": semi.location,
            "update_time": update_time_str,
            "restock_needed": bool(semi.restock_needed),
            "item_type": "semi_product"
        })

    # Apply sorting
    if sort_by == "actual_qty":
        result.sort(key=lambda x: float(x["actual_qty"] or 0), reverse=True)
    elif sort_by == "standard_qty":
        result.sort(key=lambda x: float(x["standard_qty"] or 0), reverse=True)
    elif sort_by == "update_time":
        result.sort(key=lambda x: x["update_time"] or "", reverse=True)
    else:
        # Default: sort by name
        result.sort(key=lambda x: x["ingredient_name"])

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


# ====== Semi-Product Inventory CRUD ======

def create_semi_product_inventory(
    db: Session,
    semi_product_name: str,
    unit_name: str,
    standard_qty: Optional[float],
    actual_qty: Optional[float],
    location: str
):
    """
    Create a new semi-product inventory record
    """
    from backend.models.inventory import SemiFinishedProduct, SemiProductInventory

    # Validate semi-product exists
    semi_product = db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.name == semi_product_name
    ).first()
    if not semi_product:
        raise ValueError(f"Semi-finished product '{semi_product_name}' does not exist")

    # Validate unit exists
    unit = db.query(Unit).filter(Unit.name == unit_name).first()
    if not unit:
        raise ValueError(f"Unit '{unit_name}' does not exist")

    # Validate quantities
    if standard_qty is not None and standard_qty < 0:
        raise ValueError("Standard quantity cannot be negative")
    if actual_qty is not None and actual_qty < 0:
        raise ValueError("Actual quantity cannot be negative")

    # Create inventory record
    inventory = SemiProductInventory(
        semi_product_id=semi_product.id,
        unit_id=unit.id,
        standard_qty=standard_qty if standard_qty is not None else 0,
        actual_qty=actual_qty if actual_qty is not None else 0,
        location=location,
        update_time=datetime.now(),
        restock_needed=0
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


def update_semi_product_inventory(
    db: Session,
    inventory_id: int,
    actual_qty: float
):
    """
    Update semi-product inventory actual quantity
    """
    from backend.models.inventory import SemiProductInventory

    inventory = db.query(SemiProductInventory).filter(
        SemiProductInventory.id == inventory_id
    ).first()
    if not inventory:
        return None

    # Validate quantity
    if actual_qty < 0:
        raise ValueError("Actual quantity cannot be negative")

    # Update actual_qty
    inventory.actual_qty = actual_qty
    inventory.update_time = datetime.now()

    db.commit()
    db.refresh(inventory)
    return inventory
