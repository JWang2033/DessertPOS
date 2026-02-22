from fastapi import FastAPI
from backend.routers import (
  admin_setup_router, ingredient_router,
    product_router, purchase_order_router, inventory_router
)


app = FastAPI()

# Include routers with /api prefix for frontend compatibility
app.include_router(admin_setup_router.router, prefix="/api")
app.include_router(ingredient_router.router, prefix="/api")
app.include_router(product_router.router, prefix="/api")
app.include_router(purchase_order_router.router, prefix="/api")
app.include_router(inventory_router.router, prefix="/api")