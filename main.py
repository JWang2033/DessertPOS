from fastapi import FastAPI
from backend.routers import auth, test_db, protected


app = FastAPI()

app.include_router(auth.router)
app.include_router(test_db.router)
app.include_router(protected.router)
