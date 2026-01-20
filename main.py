from fastapi import FastAPI
from backend.routers import (
    auth, protected, staff_router, test, user_router, rbac_router,
    admin_catalog_router, catalog_router, admin_setup_router, ingredient_router,
    product_router, purchase_order_router, inventory_router
)


app = FastAPI()

# Include routers with /api prefix for frontend compatibility
app.include_router(staff_router.router, prefix="/api")
app.include_router(user_router.router, prefix="/api")
app.include_router(protected.router, prefix="/api")
app.include_router(test.router, prefix="/api")
app.include_router(rbac_router.router, prefix="/api")
app.include_router(admin_catalog_router.router, prefix="/api")
app.include_router(catalog_router.router, prefix="/api")
app.include_router(admin_setup_router.router, prefix="/api")
app.include_router(ingredient_router.router, prefix="/api")
app.include_router(product_router.router, prefix="/api")
app.include_router(purchase_order_router.router, prefix="/api")
app.include_router(inventory_router.router, prefix="/api")