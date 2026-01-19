"""
Database initialization script for inventory system tables
Run this to create the new inventory-related tables in your database
"""
from backend.database import engine, Base
from backend.models.inventory import (
    Unit, Allergen, Category, CategoryUnit, IngredientRaw,
    IngredientAllergen, SemiFinishedProduct, SemiFinishedProductIngredient,
    Recipe, RecipeIngredient
)

def init_inventory_tables():
    """Create all inventory-related tables"""
    print("Creating inventory system tables...")

    # This will create tables for all models that inherit from Base
    # Only tables that don't exist will be created
    Base.metadata.create_all(bind=engine)

    print("✅ Inventory tables created successfully!")
    print("\nCreated tables:")
    print("  - units")
    print("  - allergens")
    print("  - categories")
    print("  - category_units")
    print("  - ingredients")
    print("  - ingredient_allergens")
    print("  - semi_finished_products")
    print("  - semi_finished_product_ingredients")
    print("  - recipes")
    print("  - recipe_ingredients")

if __name__ == "__main__":
    init_inventory_tables()
