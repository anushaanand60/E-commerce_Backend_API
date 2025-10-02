from fastapi import APIRouter, Depends
from app import schemas
from app.dependencies import admin_required, role_required, get_current_active_user

router=APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
def admin_dashboard(current_user=Depends(admin_required)):
    return {"message": "Welcome to admin dashboard"}

@router.get("/reports")
def view_reports(current_user=Depends(role_required("admin"))):
    return {"message": "Admin reports"}

@router.get("/profile")
def user_profile(current_user=Depends(get_current_active_user)):
    return {"user": current_user.username, "role": current_user.role}