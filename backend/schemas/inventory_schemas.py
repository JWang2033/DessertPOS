# backend/schemas/inventory_schemas.py
"""
Pydantic schemas for inventory management (admin setup)
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


# ====== Unit Schemas ======
class UnitBase(BaseModel):
    name: str = Field(..., max_length=50)
    abbreviation: str = Field(..., max_length=20)


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    abbreviation: Optional[str] = Field(None, max_length=20)


class UnitOut(UnitBase):
    id: int

    class Config:
        from_attributes = True


class UnitBatchResponse(BaseModel):
    """Response for batch unit creation"""
    created: List[UnitOut] = Field(default_factory=list, description="Successfully created units")
    skipped: List[dict] = Field(default_factory=list, description="Units that were skipped (already exist)")


# ====== Allergen Schemas ======
class AllergenBase(BaseModel):
    name: str = Field(..., max_length=100)


class AllergenCreate(AllergenBase):
    pass


class AllergenUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)


class AllergenOut(AllergenBase):
    id: int

    class Config:
        from_attributes = True


# ====== Category Schemas ======
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50, description="Category name (e.g., Fruit, Vegetable)")
    tag: Optional[str] = Field(None, max_length=100, description="Optional tag or description")


class CategoryCreate(CategoryBase):
    unit_names: List[str] = Field(..., description="List of allowed unit names (e.g., ['kg', 'lb', 'g']) for this category")


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    tag: Optional[str] = Field(None, max_length=100)
    unit_names: Optional[List[str]] = Field(None, description="Update allowed unit names")


class CategoryOut(CategoryBase):
    id: int
    units: List[UnitOut] = Field(default_factory=list, description="Allowed units for this category")

    class Config:
        from_attributes = True


# ====== Ingredient Schemas ======
class IngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    category_name: str = Field(..., description="Category name (e.g., Fruit, Vegetable)")
    brand: Optional[str] = Field(None, max_length=100)
    threshold: Optional[Decimal] = Field(None, description="Low stock threshold")


class IngredientCreate(IngredientBase):
    allergen_ids: List[int] = Field(default_factory=list, description="List of allergen IDs")


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category_name: Optional[str] = Field(None, description="Update category by name")
    brand: Optional[str] = Field(None, max_length=100)
    threshold: Optional[Decimal] = None
    allergen_ids: Optional[List[int]] = Field(None, description="Update allergen associations")


class IngredientOut(BaseModel):
    """Full ingredient output with both ID and denormalized category name"""
    id: int
    name: str
    category_id: int
    category_name: str
    brand: Optional[str]
    threshold: Optional[Decimal]
    allergens: List[AllergenOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class IngredientListOut(BaseModel):
    """Response schema for ingredient list with denormalized category and allergen names"""
    id: int
    name: str
    category_name: str
    brand: Optional[str]
    threshold: Optional[Decimal]
    allergen_names: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class IngredientBatchResponse(BaseModel):
    """Response for batch ingredient creation"""
    created: List[IngredientOut] = Field(default_factory=list, description="Successfully created ingredients")
    skipped: List[dict] = Field(default_factory=list, description="Ingredients that were skipped (already exist)")


# ====== Semi-Finished Product (Prepped Items) Schemas ======
class SemiFinishedProductIngredientBase(BaseModel):
    """Ingredient detail for semi-finished products"""
    ingredient_name: str = Field(..., description="Ingredient name")
    unit_name: str = Field(..., description="Unit name (e.g., kg, lb)")
    quantity: Decimal = Field(..., gt=0, description="Quantity must be greater than 0")


class SemiFinishedProductIngredientOut(BaseModel):
    """Response schema for ingredient details with denormalized names"""
    ingredient_id: int
    ingredient_name: str
    unit_id: int
    unit_abbreviation: str
    quantity: Decimal

    class Config:
        from_attributes = True


class SemiFinishedProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    prep_time_hours: Decimal = Field(..., gt=0, description="Preparation time in hours")


class SemiFinishedProductCreate(SemiFinishedProductBase):
    ingredients: List[SemiFinishedProductIngredientBase] = Field(..., min_items=1, description="List of ingredients")


class SemiFinishedProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    prep_time_hours: Optional[Decimal] = Field(None, gt=0)
    ingredients: Optional[List[SemiFinishedProductIngredientBase]] = Field(None, min_items=1)


class SemiFinishedProductOut(SemiFinishedProductBase):
    id: int
    ingredients: List[SemiFinishedProductIngredientOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SemiFinishedProductListOut(BaseModel):
    """Simplified list view of semi-finished products"""
    id: int
    name: str
    prep_time_hours: Decimal
    ingredient_count: int = Field(..., description="Number of ingredients")

    class Config:
        from_attributes = True


# ====== Recipe Schemas (for future use) ======
class RecipeBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: str = Field(..., max_length=50)


class RecipeOut(RecipeBase):
    id: int

    class Config:
        from_attributes = True
    id: int

    class Config:
        from_attributes = True
