# backend/routers/protected.py
from fastapi import APIRouter, Depends
from backend.utils.auth_dependencies import get_current_staff

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.get("/me")
def get_my_info(current_staff=Depends(get_current_staff)):
    return {
        "id": current_staff.id,
        "username": current_staff.username,
        "role": current_staff.role,
        "full_name": current_staff.full_name,
    }
