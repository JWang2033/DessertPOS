from fastapi import FastAPI
from backend.routers import auth, protected, staff_router, test, user_router


app = FastAPI()
app.include_router(staff_router.router)
app.include_router(user_router.router)
app.include_router(protected.router)
app.include_router(test.router)