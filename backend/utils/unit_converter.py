"""
Unit conversion utilities for inventory management
Converts between different units within the same category (weight or volume)
"""
from decimal import Decimal
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from backend.models.inventory import Unit, Category, CategoryUnit


# Conversion factors to base units (gram for weight, milliliter for volume)
WEIGHT_CONVERSIONS = {
    "kg": Decimal("1000"),      # 1 kg = 1000 g
    "g": Decimal("1"),          # 1 g = 1 g (base)
    "lb": Decimal("453.592"),   # 1 lb = 453.592 g
    "oz": Decimal("28.3495"),   # 1 oz = 28.3495 g
}

VOLUME_CONVERSIONS = {
    "mL": Decimal("1"),         # 1 mL = 1 mL (base)
    "L": Decimal("1000"),       # 1 L = 1000 mL
    "fl oz": Decimal("29.5735"), # 1 fl oz = 29.5735 mL
    "cup": Decimal("236.588"),  # 1 cup = 236.588 mL
}


def get_unit_type(abbreviation: str) -> Optional[str]:
    """
    Determine if a unit is weight or volume based on its abbreviation

    Returns:
        "weight" if it's a weight unit
        "volume" if it's a volume unit
        None if unit type cannot be determined
    """
    if abbreviation in WEIGHT_CONVERSIONS:
        return "weight"
    elif abbreviation in VOLUME_CONVERSIONS:
        return "volume"
    return None


def convert_quantity(
    quantity: Decimal,
    from_unit_abbr: str,
    to_unit_abbr: str
) -> Optional[Decimal]:
    """
    Convert quantity from one unit to another

    Args:
        quantity: The quantity to convert
        from_unit_abbr: Source unit abbreviation (e.g., "kg")
        to_unit_abbr: Target unit abbreviation (e.g., "g")

    Returns:
        Converted quantity, or None if conversion is not possible

    Example:
        convert_quantity(Decimal("2"), "kg", "g") -> Decimal("2000")
        convert_quantity(Decimal("500"), "mL", "L") -> Decimal("0.5")
    """
    from_type = get_unit_type(from_unit_abbr)
    to_type = get_unit_type(to_unit_abbr)

    # Cannot convert between different types (e.g., weight to volume)
    if from_type != to_type or from_type is None:
        return None

    # Get conversion factors
    if from_type == "weight":
        from_factor = WEIGHT_CONVERSIONS.get(from_unit_abbr)
        to_factor = WEIGHT_CONVERSIONS.get(to_unit_abbr)
    else:  # volume
        from_factor = VOLUME_CONVERSIONS.get(from_unit_abbr)
        to_factor = VOLUME_CONVERSIONS.get(to_unit_abbr)

    if from_factor is None or to_factor is None:
        return None

    # Convert: quantity * from_factor / to_factor
    # Example: 2 kg to g = 2 * 1000 / 1 = 2000 g
    base_quantity = quantity * from_factor
    converted_quantity = base_quantity / to_factor

    return converted_quantity


def can_convert_units(from_unit_abbr: str, to_unit_abbr: str) -> bool:
    """
    Check if two units can be converted to each other

    Args:
        from_unit_abbr: Source unit abbreviation
        to_unit_abbr: Target unit abbreviation

    Returns:
        True if conversion is possible, False otherwise
    """
    from_type = get_unit_type(from_unit_abbr)
    to_type = get_unit_type(to_unit_abbr)

    # Can convert if both are the same type (weight or volume)
    return from_type is not None and from_type == to_type


def find_or_create_inventory_with_conversion(
    db: Session,
    ingredient_id: int,
    purchase_unit_id: int,
    purchase_quantity: Decimal
) -> Tuple[Optional[object], Decimal]:
    """
    Find existing inventory for an ingredient and convert purchase quantity to inventory unit
    If no inventory exists, return None and the original quantity

    Args:
        db: Database session
        ingredient_id: ID of the ingredient
        purchase_unit_id: Unit ID used in the purchase order
        purchase_quantity: Quantity purchased in the purchase unit

    Returns:
        Tuple of (inventory_record or None, converted_quantity)
        If inventory exists, quantity is converted to inventory's unit
        If no inventory exists, returns (None, original_quantity)
    """
    from backend.models.inventory import Inventory

    # Get purchase unit details
    purchase_unit = db.query(Unit).filter(Unit.id == purchase_unit_id).first()
    if not purchase_unit:
        return None, purchase_quantity

    # Find any existing inventory for this ingredient
    inventory = db.query(Inventory).filter(
        Inventory.ingredient_id == ingredient_id
    ).first()

    if not inventory:
        # No existing inventory, return original quantity
        return None, purchase_quantity

    # Get inventory unit details
    inventory_unit = db.query(Unit).filter(Unit.id == inventory.unit_id).first()
    if not inventory_unit:
        return None, purchase_quantity

    # Convert quantity from purchase unit to inventory unit
    converted_qty = convert_quantity(
        purchase_quantity,
        purchase_unit.abbreviation,
        inventory_unit.abbreviation
    )

    if converted_qty is None:
        # Units are incompatible (e.g., weight vs volume), cannot convert
        # In this case, we should create a separate inventory record
        return None, purchase_quantity

    return inventory, converted_qty
