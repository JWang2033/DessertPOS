# backend/routers/ingredient_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal


router = APIRouter(prefix="/ingredients", tags=["AdminCatalog"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.post("/ingredients")
# @router.get("/ingredients")
# @router.get("/ingredients/{ingredient_id}")
# @router.put("/ingredients/{ingredient_id}")
