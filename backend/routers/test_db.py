from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal


router = APIRouter(prefix="/test", tags=["Test"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
