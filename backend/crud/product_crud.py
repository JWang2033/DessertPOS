# backend/crud/product_crud.py
"""
CRUD operations for semi-finished products (prepped items)
Phase 0 - Product preparation and recipe management
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
from backend.models.inventory import (
    SemiFinishedProduct, SemiFinishedProductIngredient,
    IngredientRaw, Unit, Category, CategoryUnit
)
from backend.schemas.inventory_schemas import (
    SemiFinishedProductCreate, SemiFinishedProductUpdate
)


# ====== Semi-Finished Product CRUD ======
def create_semi_finished_product(
    db: Session,
    payload: SemiFinishedProductCreate
) -> SemiFinishedProduct:
    """Create a semi-finished product with ingredient details"""

    # Validate prep_time_hours
    if payload.prep_time_hours <= 0:
        raise ValueError("Preparation time must be greater than 0")

    # Validate all ingredients and units exist
    ingredient_details = []
    for ing_data in payload.ingredients:
        # Get ingredient by name
        ingredient = db.query(IngredientRaw).filter(
            IngredientRaw.name == ing_data.ingredient_name
        ).first()
        if not ingredient:
            raise ValueError(f"Ingredient '{ing_data.ingredient_name}' does not exist")

        # Get unit by name
        unit = db.query(Unit).filter(Unit.name == ing_data.unit_name).first()
        if not unit:
            raise ValueError(f"Unit '{ing_data.unit_name}' does not exist")

        # Optional: Validate unit is allowed for ingredient's category
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
        if ing_data.quantity <= 0:
            raise ValueError(f"Quantity for '{ing_data.ingredient_name}' must be greater than 0")

        ingredient_details.append({
            "ingredient_id": ingredient.id,
            "unit_id": unit.id,
            "quantity": ing_data.quantity
        })

    # Create semi-finished product
    product = SemiFinishedProduct(
        name=payload.name,
        prep_time_hours=payload.prep_time_hours
    )
    db.add(product)
    db.flush()  # Get the ID

    # Create ingredient associations
    for detail in ingredient_details:
        assoc = SemiFinishedProductIngredient(
            semi_finished_product_id=product.id,
            ingredient_id=detail["ingredient_id"],
            unit_id=detail["unit_id"],
            quantity=detail["quantity"]
        )
        db.add(assoc)

    db.commit()
    db.refresh(product)
    return product


def get_semi_finished_product_by_id(
    db: Session,
    product_id: int
) -> Optional[SemiFinishedProduct]:
    """Get semi-finished product by ID"""
    return db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.id == product_id
    ).first()


def get_semi_finished_product_by_name(
    db: Session,
    name: str
) -> Optional[SemiFinishedProduct]:
    """Get semi-finished product by name"""
    return db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.name == name
    ).first()


def get_semi_finished_product_ingredients(
    db: Session,
    product_id: int
) -> List[dict]:
    """Get all ingredients for a semi-finished product with denormalized data"""
    ingredients = db.query(
        SemiFinishedProductIngredient.ingredient_id,
        SemiFinishedProductIngredient.unit_id,
        SemiFinishedProductIngredient.quantity,
        IngredientRaw.name.label("ingredient_name"),
        Unit.abbreviation.label("unit_abbreviation")
    ).join(
        IngredientRaw,
        SemiFinishedProductIngredient.ingredient_id == IngredientRaw.id
    ).join(
        Unit,
        SemiFinishedProductIngredient.unit_id == Unit.id
    ).filter(
        SemiFinishedProductIngredient.semi_finished_product_id == product_id
    ).all()

    return [
        {
            "ingredient_id": ing.ingredient_id,
            "ingredient_name": ing.ingredient_name,
            "unit_id": ing.unit_id,
            "unit_abbreviation": ing.unit_abbreviation,
            "quantity": ing.quantity
        }
        for ing in ingredients
    ]


def list_semi_finished_products(
    db: Session,
    name_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    List semi-finished products with optional name filter.
    Returns simplified view with ingredient count.
    """
    query = db.query(SemiFinishedProduct)

    if name_filter:
        query = query.filter(SemiFinishedProduct.name.like(f"%{name_filter}%"))

    products = query.offset(skip).limit(limit).all()

    result = []
    for product in products:
        # Count ingredients
        ingredient_count = db.query(SemiFinishedProductIngredient).filter(
            SemiFinishedProductIngredient.semi_finished_product_id == product.id
        ).count()

        result.append({
            "id": product.id,
            "name": product.name,
            "prep_time_hours": product.prep_time_hours,
            "ingredient_count": ingredient_count
        })

    return result


def update_semi_finished_product(
    db: Session,
    product_id: int,
    payload: SemiFinishedProductUpdate
) -> Optional[SemiFinishedProduct]:
    """Update a semi-finished product"""
    product = db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.id == product_id
    ).first()
    if not product:
        return None

    # Update basic fields
    if payload.name is not None:
        # Check name uniqueness
        existing = db.query(SemiFinishedProduct).filter(
            SemiFinishedProduct.name == payload.name,
            SemiFinishedProduct.id != product_id
        ).first()
        if existing:
            raise ValueError(f"Semi-finished product with name '{payload.name}' already exists")
        product.name = payload.name

    if payload.prep_time_hours is not None:
        if payload.prep_time_hours <= 0:
            raise ValueError("Preparation time must be greater than 0")
        product.prep_time_hours = payload.prep_time_hours

    # Update ingredients if provided
    if payload.ingredients is not None:
        # Validate all ingredients and units
        ingredient_details = []
        for ing_data in payload.ingredients:
            # Get ingredient by name
            ingredient = db.query(IngredientRaw).filter(
                IngredientRaw.name == ing_data.ingredient_name
            ).first()
            if not ingredient:
                raise ValueError(f"Ingredient '{ing_data.ingredient_name}' does not exist")

            # Get unit by name
            unit = db.query(Unit).filter(Unit.name == ing_data.unit_name).first()
            if not unit:
                raise ValueError(f"Unit '{ing_data.unit_name}' does not exist")

            # Optional: Validate unit is allowed for ingredient's category
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
            if ing_data.quantity <= 0:
                raise ValueError(f"Quantity for '{ing_data.ingredient_name}' must be greater than 0")

            ingredient_details.append({
                "ingredient_id": ingredient.id,
                "unit_id": unit.id,
                "quantity": ing_data.quantity
            })

        # Clear existing ingredient associations
        db.query(SemiFinishedProductIngredient).filter(
            SemiFinishedProductIngredient.semi_finished_product_id == product_id
        ).delete()

        # Add new ingredient associations
        for detail in ingredient_details:
            assoc = SemiFinishedProductIngredient(
                semi_finished_product_id=product_id,
                ingredient_id=detail["ingredient_id"],
                unit_id=detail["unit_id"],
                quantity=detail["quantity"]
            )
            db.add(assoc)

    db.commit()
    db.refresh(product)
    return product


def update_semi_finished_product_by_name(
    db: Session,
    name: str,
    payload: SemiFinishedProductUpdate
) -> Optional[SemiFinishedProduct]:
    """Update a semi-finished product by name"""
    product = db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.name == name
    ).first()
    if not product:
        return None

    return update_semi_finished_product(db, product.id, payload)


def delete_semi_finished_product(
    db: Session,
    product_id: int
) -> bool:
    """Delete a semi-finished product and its ingredient associations"""
    product = db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.id == product_id
    ).first()
    if not product:
        return False

    # Delete ingredient associations first
    db.query(SemiFinishedProductIngredient).filter(
        SemiFinishedProductIngredient.semi_finished_product_id == product_id
    ).delete()

    # Delete the product
    db.delete(product)
    db.commit()
    return True


def delete_semi_finished_product_by_name(
    db: Session,
    name: str
) -> bool:
    """Delete a semi-finished product by name"""
    product = db.query(SemiFinishedProduct).filter(
        SemiFinishedProduct.name == name
    ).first()
    if not product:
        return False

    return delete_semi_finished_product(db, product.id)
