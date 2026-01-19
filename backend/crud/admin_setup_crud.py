# backend/crud/admin_setup_crud.py
"""
CRUD operations for admin setup (categories, units, allergens)
Phase 0 / Infrequent updates
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.inventory import (
    Unit, Allergen, Category, CategoryUnit
)
from backend.schemas.inventory_schemas import (
    UnitCreate, UnitUpdate,
    AllergenCreate, AllergenUpdate,
    CategoryCreate, CategoryUpdate
)


# ====== Unit CRUD ======
def create_unit(db: Session, payload: UnitCreate) -> Unit:
    """Create a new unit of measurement"""
    obj = Unit(name=payload.name, abbreviation=payload.abbreviation)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_units_batch(db: Session, payloads: List[UnitCreate]) -> dict:
    """
    Create multiple units at once, skipping any that already exist.
    Returns dict with created units and skipped units.
    """
    created_units = []
    skipped_units = []

    for payload in payloads:
        # Check if unit already exists
        existing = db.query(Unit).filter(Unit.name == payload.name).first()
        if existing:
            skipped_units.append({
                "name": payload.name,
                "abbreviation": payload.abbreviation,
                "reason": "already exists"
            })
            continue

        obj = Unit(name=payload.name, abbreviation=payload.abbreviation)
        db.add(obj)
        created_units.append(obj)

    db.commit()

    # Refresh all created units
    for unit in created_units:
        db.refresh(unit)

    return {
        "created": created_units,
        "skipped": skipped_units
    }


def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
    """Get unit by ID"""
    return db.query(Unit).filter(Unit.id == unit_id).first()


def get_unit_by_name(db: Session, name: str) -> Optional[Unit]:
    """Get unit by name"""
    return db.query(Unit).filter(Unit.name == name).first()


def list_units(db: Session, skip: int = 0, limit: int = 100) -> List[Unit]:
    """List all units"""
    return db.query(Unit).offset(skip).limit(limit).all()


def update_unit(db: Session, unit_id: int, payload: UnitUpdate) -> Optional[Unit]:
    """Update an existing unit"""
    obj = db.query(Unit).filter(Unit.id == unit_id).first()
    if not obj:
        return None

    if payload.name is not None:
        obj.name = payload.name
    if payload.abbreviation is not None:
        obj.abbreviation = payload.abbreviation

    db.commit()
    db.refresh(obj)
    return obj


def update_unit_by_name(db: Session, name: str, payload: UnitUpdate) -> Optional[Unit]:
    """Update an existing unit by name"""
    obj = db.query(Unit).filter(Unit.name == name).first()
    if not obj:
        return None

    if payload.name is not None:
        obj.name = payload.name
    if payload.abbreviation is not None:
        obj.abbreviation = payload.abbreviation

    db.commit()
    db.refresh(obj)
    return obj


def delete_unit(db: Session, unit_id: int) -> bool:
    """Delete a unit"""
    obj = db.query(Unit).filter(Unit.id == unit_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def delete_unit_by_name(db: Session, name: str) -> bool:
    """Delete a unit by name"""
    obj = db.query(Unit).filter(Unit.name == name).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ====== Allergen CRUD ======
def create_allergen(db: Session, payload: AllergenCreate) -> Allergen:
    """Create a new allergen"""
    obj = Allergen(name=payload.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_allergen_by_id(db: Session, allergen_id: int) -> Optional[Allergen]:
    """Get allergen by ID"""
    return db.query(Allergen).filter(Allergen.id == allergen_id).first()


def get_allergen_by_name(db: Session, name: str) -> Optional[Allergen]:
    """Get allergen by name"""
    return db.query(Allergen).filter(Allergen.name == name).first()


def list_allergens(db: Session, skip: int = 0, limit: int = 100) -> List[Allergen]:
    """List all allergens"""
    return db.query(Allergen).offset(skip).limit(limit).all()


def update_allergen(db: Session, allergen_id: int, payload: AllergenUpdate) -> Optional[Allergen]:
    """Update an existing allergen"""
    obj = db.query(Allergen).filter(Allergen.id == allergen_id).first()
    if not obj:
        return None

    if payload.name is not None:
        obj.name = payload.name

    db.commit()
    db.refresh(obj)
    return obj


def delete_allergen(db: Session, allergen_id: int) -> bool:
    """Delete an allergen"""
    obj = db.query(Allergen).filter(Allergen.id == allergen_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ====== Category CRUD ======
def create_category(db: Session, payload: CategoryCreate) -> Category:
    """
    Create or update a category with associated units.
    If category name exists, update it; otherwise create new.
    Accepts unit names and automatically looks up their IDs.
    """
    # Check if category already exists
    existing = db.query(Category).filter(Category.name == payload.name).first()

    if existing:
        # Update existing category
        existing.tag = payload.tag
        category = existing

        # Clear existing category_units relationships
        db.query(CategoryUnit).filter(CategoryUnit.category_id == category.id).delete()
    else:
        # Create new category
        category = Category(name=payload.name, tag=payload.tag)
        db.add(category)
        db.flush()  # Get the ID before adding relationships

    # Convert unit names to unit IDs and validate they exist
    unit_ids = []
    for unit_name in payload.unit_names:
        unit = db.query(Unit).filter(Unit.name == unit_name).first()
        if not unit:
            db.rollback()
            raise ValueError(f"Unit with name '{unit_name}' does not exist in the units table")
        unit_ids.append(unit.id)

    # Add new category_units relationships
    for unit_id in unit_ids:
        category_unit = CategoryUnit(category_id=category.id, unit_id=unit_id)
        db.add(category_unit)

    db.commit()
    db.refresh(category)
    return category
def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    """Get category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """Get category by name"""
    return db.query(Category).filter(Category.name == name).first()


def list_categories(
    db: Session,
    name_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    List all categories with their associated units.
    Optionally filter by name (fuzzy search).

    Returns a list of dicts with category info and units list.
    """
    query = db.query(Category)

    if name_filter:
        query = query.filter(Category.name.like(f"%{name_filter}%"))

    categories = query.offset(skip).limit(limit).all()

    result = []
    for category in categories:
        # Get associated units
        unit_ids = db.query(CategoryUnit.unit_id).filter(
            CategoryUnit.category_id == category.id
        ).all()
        unit_ids = [u[0] for u in unit_ids]

        units = db.query(Unit).filter(Unit.id.in_(unit_ids)).all() if unit_ids else []

        result.append({
            "id": category.id,
            "name": category.name,
            "tag": category.tag,
            "units": units
        })

    return result


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Optional[Category]:
    """Update an existing category"""
    obj = db.query(Category).filter(Category.id == category_id).first()
    if not obj:
        return None

    if payload.name is not None:
        obj.name = payload.name
    if payload.tag is not None:
        obj.tag = payload.tag

    # Update unit associations if provided
    if payload.unit_names is not None:
        # Convert unit names to IDs and validate they exist
        unit_ids = []
        for unit_name in payload.unit_names:
            unit = db.query(Unit).filter(Unit.name == unit_name).first()
            if not unit:
                db.rollback()
                raise ValueError(f"Unit with name '{unit_name}' does not exist in the units table")
            unit_ids.append(unit.id)

        # Clear existing relationships
        db.query(CategoryUnit).filter(CategoryUnit.category_id == category_id).delete()

        # Add new relationships
        for unit_id in unit_ids:
            category_unit = CategoryUnit(category_id=category_id, unit_id=unit_id)
            db.add(category_unit)

    db.commit()
    db.refresh(obj)
    return obj


def update_category_by_name(db: Session, name: str, payload: CategoryUpdate) -> Optional[Category]:
    """Update an existing category by name"""
    obj = db.query(Category).filter(Category.name == name).first()
    if not obj:
        return None

    if payload.name is not None:
        obj.name = payload.name
    if payload.tag is not None:
        obj.tag = payload.tag

    # Update unit associations if provided
    if payload.unit_names is not None:
        # Convert unit names to IDs and validate they exist
        unit_ids = []
        for unit_name in payload.unit_names:
            unit = db.query(Unit).filter(Unit.name == unit_name).first()
            if not unit:
                db.rollback()
                raise ValueError(f"Unit with name '{unit_name}' does not exist in the units table")
            unit_ids.append(unit.id)

        # Clear existing relationships
        db.query(CategoryUnit).filter(CategoryUnit.category_id == obj.id).delete()

        # Add new relationships
        for unit_id in unit_ids:
            category_unit = CategoryUnit(category_id=obj.id, unit_id=unit_id)
            db.add(category_unit)

    db.commit()
    db.refresh(obj)
    return obj


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category and its unit associations"""
    obj = db.query(Category).filter(Category.id == category_id).first()
    if not obj:
        return False

    # Delete category_units relationships first
    db.query(CategoryUnit).filter(CategoryUnit.category_id == category_id).delete()

    # Delete the category
    db.delete(obj)
    db.commit()
    return True


def delete_category_by_name(db: Session, name: str) -> bool:
    """Delete a category and its unit associations by name"""
    obj = db.query(Category).filter(Category.name == name).first()
    if not obj:
        return False

    # Delete category_units relationships first
    db.query(CategoryUnit).filter(CategoryUnit.category_id == obj.id).delete()

    # Delete the category
    db.delete(obj)
    db.commit()
    return True


def get_category_units(db: Session, category_id: int) -> List[Unit]:
    """Get all units allowed for a specific category"""
    unit_ids = db.query(CategoryUnit.unit_id).filter(
        CategoryUnit.category_id == category_id
    ).all()
    unit_ids = [u[0] for u in unit_ids]

    if not unit_ids:
        return []

    return db.query(Unit).filter(Unit.id.in_(unit_ids)).all()
