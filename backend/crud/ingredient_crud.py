# backend/crud/ingredient_crud.py
"""
CRUD operations for ingredients
Phase 0 / Phase 1 - Ingredient management
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.models.inventory import (
    IngredientRaw, Category, Allergen, IngredientAllergen
)
from backend.schemas.inventory_schemas import (
    IngredientCreate, IngredientUpdate
)


# ====== Ingredient CRUD ======
def create_ingredient(db: Session, payload: IngredientCreate) -> IngredientRaw:
    """Create a single ingredient with allergen associations"""
    # Validate category exists by name
    category = db.query(Category).filter(Category.name == payload.category_name).first()
    if not category:
        raise ValueError(f"Category with name '{payload.category_name}' does not exist")

    # Validate unit exists by name
    from backend.models.inventory import Unit
    unit = db.query(Unit).filter(Unit.name == payload.unit_name).first()
    if not unit:
        raise ValueError(f"Unit with name '{payload.unit_name}' does not exist")

    # Validate allergen IDs exist
    if payload.allergen_ids:
        allergen_count = db.query(Allergen).filter(
            Allergen.id.in_(payload.allergen_ids)
        ).count()
        if allergen_count != len(payload.allergen_ids):
            raise ValueError("One or more allergen IDs do not exist")

    # Validate threshold if provided
    if payload.threshold is not None and payload.threshold <= 0:
        raise ValueError("Threshold must be greater than 0")

    # Create ingredient
    ingredient = IngredientRaw(
        name=payload.name,
        category_id=category.id,
        unit_id=unit.id,
        brand=payload.brand,
        threshold=payload.threshold
    )
    db.add(ingredient)
    db.flush()  # Get the ID without committing

    # Create allergen associations
    for allergen_id in payload.allergen_ids:
        assoc = IngredientAllergen(
            ingredient_id=ingredient.id,
            allergen_id=allergen_id
        )
        db.add(assoc)

    db.commit()
    db.refresh(ingredient)
    return ingredient


def create_ingredients_batch(db: Session, payloads: List[IngredientCreate]) -> dict:
    """
    Create multiple ingredients at once, skipping any that already exist.
    Returns dict with created ingredients and skipped ingredients.
    """
    created_ingredients = []
    skipped_ingredients = []

    for payload in payloads:
        # Check if ingredient already exists
        existing = db.query(IngredientRaw).filter(
            IngredientRaw.name == payload.name
        ).first()
        if existing:
            skipped_ingredients.append({
                "name": payload.name,
                "reason": "already exists"
            })
            continue

        try:
            ingredient = create_ingredient(db, payload)
            created_ingredients.append(ingredient)
        except ValueError as e:
            skipped_ingredients.append({
                "name": payload.name,
                "reason": str(e)
            })

    return {
        "created": created_ingredients,
        "skipped": skipped_ingredients
    }


def get_ingredient_by_id(db: Session, ingredient_id: int) -> Optional[IngredientRaw]:
    """Get ingredient by ID"""
    return db.query(IngredientRaw).filter(IngredientRaw.id == ingredient_id).first()


def get_ingredient_by_name(db: Session, name: str) -> Optional[IngredientRaw]:
    """Get ingredient by name"""
    return db.query(IngredientRaw).filter(IngredientRaw.name == name).first()


def get_ingredient_allergens(db: Session, ingredient_id: int) -> List[Allergen]:
    """Get all allergens for a specific ingredient"""
    allergen_ids = db.query(IngredientAllergen.allergen_id).filter(
        IngredientAllergen.ingredient_id == ingredient_id
    ).all()
    allergen_ids = [a[0] for a in allergen_ids]

    if not allergen_ids:
        return []

    return db.query(Allergen).filter(Allergen.id.in_(allergen_ids)).all()


def list_ingredients(
    db: Session,
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    List all ingredients with optional filtering.
    Returns list of dicts with denormalized data (category_name, allergen_names).

    Args:
        q: Name fuzzy search
        category_id: Filter by category
        skip: Pagination offset
        limit: Max results
    """
    query = db.query(IngredientRaw)

    # Apply filters
    if q:
        query = query.filter(IngredientRaw.name.like(f"%{q}%"))

    if category_id:
        query = query.filter(IngredientRaw.category_id == category_id)

    ingredients = query.offset(skip).limit(limit).all()

    # Build result with denormalized data
    result = []
    for ingredient in ingredients:
        # Get category name
        category = db.query(Category).filter(
            Category.id == ingredient.category_id
        ).first()
        category_name = category.name if category else "Unknown"

        # Get unit name
        from backend.models.inventory import Unit
        unit = db.query(Unit).filter(
            Unit.id == ingredient.unit_id
        ).first()
        unit_name = unit.name if unit else "Unknown"

        # Get allergen names
        from backend.models.inventory import Unit
        unit = db.query(Unit).filter(
            Unit.id == ingredient.unit_id
        ).first()
        unit_name = unit.name if unit else "Unknown"

        # Get allergen names
        allergen_ids = db.query(IngredientAllergen.allergen_id).filter(
            IngredientAllergen.ingredient_id == ingredient.id
        ).all()
        allergen_ids = [a[0] for a in allergen_ids]

        allergens = []
        if allergen_ids:
            allergens = db.query(Allergen).filter(
                Allergen.id.in_(allergen_ids)
            ).all()

        allergen_names = [a.name for a in allergens]

        result.append({
            "id": ingredient.id,
            "name": ingredient.name,
            "category_id": ingredient.category_id,
            "category_name": category_name,
            "unit_name": unit_name,
            "brand": ingredient.brand,
            "threshold": ingredient.threshold,
            "allergen_names": allergen_names
        })

    return result


def update_ingredient(
    db: Session,
    ingredient_id: int,
    payload: IngredientUpdate
) -> Optional[IngredientRaw]:
    """Update an existing ingredient"""
    ingredient = db.query(IngredientRaw).filter(
        IngredientRaw.id == ingredient_id
    ).first()
    if not ingredient:
        return None

    # Validate category if being updated
    if payload.category_id is not None:
        category = db.query(Category).filter(
            Category.id == payload.category_id
        ).first()
        if not category:
            raise ValueError(f"Category with id {payload.category_id} does not exist")
        ingredient.category_id = payload.category_id

    # Validate threshold if being updated
    if payload.threshold is not None and payload.threshold <= 0:
        raise ValueError("Threshold must be greater than 0")

    # Update basic fields
    if payload.name is not None:
        # Check name uniqueness
        existing = db.query(IngredientRaw).filter(
            IngredientRaw.name == payload.name,
            IngredientRaw.id != ingredient_id
        ).first()
        if existing:
            raise ValueError(f"Ingredient with name '{payload.name}' already exists")
        ingredient.name = payload.name

    if payload.brand is not None:
        ingredient.brand = payload.brand

    if payload.threshold is not None:
        ingredient.threshold = payload.threshold

    # Update allergen associations if provided
    if payload.allergen_ids is not None:
        # Validate allergen IDs
        allergen_count = db.query(Allergen).filter(
            Allergen.id.in_(payload.allergen_ids)
        ).count()
        if allergen_count != len(payload.allergen_ids):
            raise ValueError("One or more allergen IDs do not exist")

        # Clear existing associations
        db.query(IngredientAllergen).filter(
            IngredientAllergen.ingredient_id == ingredient_id
        ).delete()

        # Add new associations
        for allergen_id in payload.allergen_ids:
            assoc = IngredientAllergen(
                ingredient_id=ingredient_id,
                allergen_id=allergen_id
            )
            db.add(assoc)

    db.commit()
    db.refresh(ingredient)
    return ingredient


def update_ingredient_by_name(
    db: Session,
    name: str,
    payload: IngredientUpdate
) -> Optional[IngredientRaw]:
    """Update an existing ingredient by name"""
    ingredient = db.query(IngredientRaw).filter(
        IngredientRaw.name == name
    ).first()
    if not ingredient:
        return None

    # Validate category if being updated (by name)
    if payload.category_name is not None:
        category = db.query(Category).filter(
            Category.name == payload.category_name
        ).first()
        if not category:
            raise ValueError(f"Category with name '{payload.category_name}' does not exist")
        ingredient.category_id = category.id

    # Validate threshold if being updated
    if payload.threshold is not None and payload.threshold <= 0:
        raise ValueError("Threshold must be greater than 0")

    # Update basic fields
    if payload.name is not None:
        # Check name uniqueness
        existing = db.query(IngredientRaw).filter(
            IngredientRaw.name == payload.name,
            IngredientRaw.id != ingredient.id
        ).first()
        if existing:
            raise ValueError(f"Ingredient with name '{payload.name}' already exists")
        ingredient.name = payload.name

    if payload.brand is not None:
        ingredient.brand = payload.brand

    if payload.threshold is not None:
        ingredient.threshold = payload.threshold

    # Update allergen associations if provided
    if payload.allergen_ids is not None:
        # Validate allergen IDs
        allergen_count = db.query(Allergen).filter(
            Allergen.id.in_(payload.allergen_ids)
        ).count()
        if allergen_count != len(payload.allergen_ids):
            raise ValueError("One or more allergen IDs do not exist")

        # Clear existing associations
        db.query(IngredientAllergen).filter(
            IngredientAllergen.ingredient_id == ingredient.id
        ).delete()

        # Add new associations
        for allergen_id in payload.allergen_ids:
            assoc = IngredientAllergen(
                ingredient_id=ingredient.id,
                allergen_id=allergen_id
            )
            db.add(assoc)

    db.commit()
    db.refresh(ingredient)
    return ingredient


def delete_ingredient(db: Session, ingredient_id: int) -> bool:
    """Delete an ingredient and its allergen associations"""
    ingredient = db.query(IngredientRaw).filter(
        IngredientRaw.id == ingredient_id
    ).first()
    if not ingredient:
        return False

    # Delete allergen associations first
    db.query(IngredientAllergen).filter(
        IngredientAllergen.ingredient_id == ingredient_id
    ).delete()

    # Delete the ingredient
    db.delete(ingredient)
    db.commit()
    return True


def delete_ingredient_by_name(db: Session, name: str) -> bool:
    """Delete an ingredient and its allergen associations by name"""
    ingredient = db.query(IngredientRaw).filter(
        IngredientRaw.name == name
    ).first()
    if not ingredient:
        return False

    # Delete allergen associations first
    db.query(IngredientAllergen).filter(
        IngredientAllergen.ingredient_id == ingredient.id
    ).delete()

    # Delete the ingredient
    db.delete(ingredient)
    db.commit()
    return True
