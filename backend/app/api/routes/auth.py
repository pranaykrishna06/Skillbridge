from app.core.dependencies import require_role
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import get_current_user
from fastapi import Depends

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

from app.services.auth_service import register_user, login_user


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):

    if data.role.lower() not in ["student", "recruiter"]:
        raise HTTPException(
            status_code=400,
            detail="Only Student and Recruiter registration is allowed."
        )

    user = register_user(
        data.full_name,
        data.email,
        data.password,
        data.role
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid role or email already registered."
        )

    return {
        "message": "Registration successful",
        "user": user
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):

    result = login_user(data.email, data.password)

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return result
@router.get("/me")
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "Authenticated successfully",
        "user": current_user
    }
@router.get("/student-only")
def student_only(
    current_user: dict = Depends(require_role("Student"))
):
    return {
        "message": "Student access granted",
        "user": current_user
    }


@router.get("/recruiter-only")
def recruiter_only(
    current_user: dict = Depends(require_role("Recruiter"))
):
    return {
        "message": "Recruiter access granted",
        "user": current_user
    }


@router.get("/admin-only")
def admin_only(
    current_user: dict = Depends(require_role("Admin"))
):
    return {
        "message": "Admin access granted",
        "user": current_user
    }
