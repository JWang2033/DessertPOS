# backend/models/inventory.py
"""
Inventory system models for ingredients, categories, units, allergens, etc.
Based on create-table-template.sql structure
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.database import Base


class Unit(Base):
    """Units of measurement (e.g., kg, lb, oz, g, L, ml)"""
    __tablename__ = "units"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    abbreviation = Column(String(20), nullable=False)


class Allergen(Base):
    """Common allergens (e.g., milk, nuts, gluten, soy)"""
    __tablename__ = "allergens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


class Category(Base):
    """Ingredient categories (e.g., Fruit, Vegetable, Dairy, Meat)"""
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    tag = Column(String(100), nullable=True)


class CategoryUnit(Base):
    """Many-to-many relationship between categories and allowed units"""
    __tablename__ = "category_units"

    category_id = Column(BigInteger, ForeignKey("categories.id"), primary_key=True)
    unit_id = Column(BigInteger, ForeignKey("units.id"), primary_key=True)


class IngredientRaw(Base):
    """Raw ingredients with inventory tracking"""
    __tablename__ = "ingredients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)
    brand = Column(String(100), nullable=True)
    threshold = Column(DECIMAL(10, 2), nullable=True, comment="Low stock threshold")


class IngredientAllergen(Base):
    """Many-to-many relationship between ingredients and allergens"""
    __tablename__ = "ingredient_allergens"

    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id"), primary_key=True)
    allergen_id = Column(BigInteger, ForeignKey("allergens.id"), primary_key=True)


class SemiFinishedProduct(Base):
    """Semi-finished products prepared in advance (e.g., pre-made dough, sauce)"""
    __tablename__ = "semi_finished_products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    prep_time_hours = Column(DECIMAL(5, 2), nullable=False, comment="Preparation time in hours")


class SemiFinishedProductIngredient(Base):
    """Ingredients required for semi-finished products"""
    __tablename__ = "semi_finished_product_ingredients"

    semi_finished_product_id = Column(BigInteger, ForeignKey("semi_finished_products.id"), primary_key=True)
    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id"), primary_key=True)
    unit_id = Column(BigInteger, ForeignKey("units.id"), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)


class Recipe(Base):
    """Recipes for final products"""
    __tablename__ = "recipes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)


class RecipeIngredient(Base):
    """Ingredients required for recipes"""
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(BigInteger, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id"), primary_key=True)
    unit_id = Column(BigInteger, ForeignKey("units.id"), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
