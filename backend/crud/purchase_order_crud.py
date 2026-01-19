# backend/crud/purchase_order_crud.py
"""
CRUD operations for purchase orders (receiving)
Phase 0/1 - Inventory receiving and tracking
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, datetime
from backend.models.inventory import (
    PurchaseOrder, PurchaseOrderItem,
    IngredientRaw, Unit, Category, CategoryUnit
)
from backend.schemas.inventory_schemas import (
    PurchaseOrderCreate, PurchaseOrderItemCreate
)


def generate_po_code(db: Session, order_date: str) -> str:
    """
    Generate unique PO code in format: PO-YYYYMMDD-NNNN

    Args:
        db: Database session
        order_date: Date string in YYYY-MM-DD format

    Returns:
        Unique PO code like "PO-20260119-0001"
    """
    # Convert date format: 2026-01-19 -> 20260119
    date_part = order_date.replace("-", "")

    # Find the highest sequence number for this date
    prefix = f"PO-{date_part}-"
    existing_codes = db.query(PurchaseOrder.po_code).filter(
        PurchaseOrder.po_code.like(f"{prefix}%")
    ).all()

    if not existing_codes:
        sequence = 1
    else:
        # Extract sequence numbers and find max
        sequences = []
        for (code,) in existing_codes:
            try:
                seq_str = code.split("-")[-1]
                sequences.append(int(seq_str))
            except (ValueError, IndexError):
                continue

        sequence = max(sequences) + 1 if sequences else 1

    return f"{prefix}{sequence:04d}"


def create_purchase_order(
    db: Session,
    payload: PurchaseOrderCreate
) -> PurchaseOrder:
    """
    Create a purchase order with items

    Validation:
    - order_date must be <= today
    - Each ingredient must exist
    - Each quantity must be > 0
    - Unit must be compatible with ingredient's category
    """
    # Validate order_date
    try:
        order_date_obj = datetime.strptime(payload.order_date, "%Y-%m-%d").date()
        if order_date_obj > date.today():
            raise ValueError(f"Order date cannot be in the future. Today is {date.today()}")
    except ValueError as e:
        if "does not match format" in str(e):
            raise ValueError("Order date must be in YYYY-MM-DD format")
        raise

    # Validate all items before creating order
    item_details = []
    for item_data in payload.items:
        # Get ingredient by name
        ingredient = db.query(IngredientRaw).filter(
            IngredientRaw.name == item_data.ingredient_name
        ).first()
        if not ingredient:
            raise ValueError(f"Ingredient '{item_data.ingredient_name}' does not exist")

        # Get unit by name
        unit = db.query(Unit).filter(Unit.name == item_data.unit_name).first()
        if not unit:
            raise ValueError(f"Unit '{item_data.unit_name}' does not exist")

        # Validate unit is allowed for ingredient's category
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

        # Validate quantity
        if item_data.quantity <= 0:
            raise ValueError(f"Quantity for '{item_data.ingredient_name}' must be greater than 0")

        item_details.append({
            "ingredient_id": ingredient.id,
            "unit_id": unit.id,
            "quantity": item_data.quantity,
            "vendor": item_data.vendor
        })

    # Generate unique PO code
    po_code = generate_po_code(db, payload.order_date)

    # Create purchase order header
    po = PurchaseOrder(
        po_code=po_code,
        order_date=payload.order_date,
        store_id=payload.store_id
    )
    db.add(po)
    db.flush()  # Get the ID

    # Create purchase order items
    for detail in item_details:
        item = PurchaseOrderItem(
            purchase_order_id=po.id,
            ingredient_id=detail["ingredient_id"],
            unit_id=detail["unit_id"],
            quantity=detail["quantity"],
            vendor=detail["vendor"]
        )
        db.add(item)

    db.commit()
    db.refresh(po)
    return po


def list_purchase_orders(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    store_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    List purchase orders with optional filters

    Returns simplified view with total_items_count
    """
    query = db.query(PurchaseOrder)

    # Apply filters
    if date_from:
        query = query.filter(PurchaseOrder.order_date >= date_from)

    if date_to:
        query = query.filter(PurchaseOrder.order_date <= date_to)

    if store_id:
        query = query.filter(PurchaseOrder.store_id == store_id)

    # Order by date descending (newest first)
    query = query.order_by(PurchaseOrder.order_date.desc(), PurchaseOrder.po_code.desc())

    pos = query.offset(skip).limit(limit).all()

    result = []
    for po in pos:
        # Count items
        item_count = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.purchase_order_id == po.id
        ).count()

        # Convert date to string if it's a date object
        order_date_str = po.order_date if isinstance(po.order_date, str) else po.order_date.isoformat()

        result.append({
            "id": po.id,
            "po_code": po.po_code,
            "order_date": order_date_str,
            "store_id": po.store_id,
            "total_items_count": item_count
        })

    return result


def get_purchase_order_by_code(
    db: Session,
    po_code: str
) -> Optional[PurchaseOrder]:
    """Get purchase order by PO code"""
    return db.query(PurchaseOrder).filter(
        PurchaseOrder.po_code == po_code
    ).first()


def get_purchase_order_items(
    db: Session,
    po_id: int
) -> List[dict]:
    """
    Get all items for a purchase order with denormalized data

    Returns:
        List of items with ingredient_name, quantity, unit_abbreviation, vendor
    """
    items = db.query(
        PurchaseOrderItem.id,
        PurchaseOrderItem.ingredient_id,
        PurchaseOrderItem.unit_id,
        PurchaseOrderItem.quantity,
        PurchaseOrderItem.vendor,
        IngredientRaw.name.label("ingredient_name"),
        Unit.abbreviation.label("unit_abbreviation")
    ).join(
        IngredientRaw,
        PurchaseOrderItem.ingredient_id == IngredientRaw.id
    ).join(
        Unit,
        PurchaseOrderItem.unit_id == Unit.id
    ).filter(
        PurchaseOrderItem.purchase_order_id == po_id
    ).all()

    return [
        {
            "id": item.id,
            "ingredient_id": item.ingredient_id,
            "ingredient_name": item.ingredient_name,
            "unit_id": item.unit_id,
            "unit_abbreviation": item.unit_abbreviation,
            "quantity": item.quantity,
            "vendor": item.vendor
        }
        for item in items
    ]
