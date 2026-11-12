from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_role

from app.schemas.recruiter import (
    CompanyCreate,
    CompanyUpdate,
    RecruiterUpdate
)

from app.services.recruiter_service import (
    create_company,
    get_company,
    update_company,
    get_recruiter_profile,
    update_recruiter_profile
)


router = APIRouter(
    prefix="/api/recruiters",
    tags=["Recruiter"]
)


# ==========================================
# REGISTER COMPANY
# ==========================================

@router.post("/company", status_code=status.HTTP_201_CREATED)
def register_company(
    data: CompanyCreate,
    current_user: dict = Depends(require_role("Recruiter"))
):

    try:
        company_id = create_company(
            current_user["user_id"],
            data
        )

        if company_id is None:
            raise HTTPException(
                status_code=409,
                detail="Recruiter is already associated with a company."
            )

        return {
            "message": "Company registered successfully.",
            "company_id": company_id
        }

    except HTTPException:
        raise

    except Exception as error:

        if getattr(error, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=409,
                detail="Company registration number already exists."
            )

        raise


# ==========================================
# VIEW COMPANY
# ==========================================

@router.get("/company")
def view_company(
    current_user: dict = Depends(require_role("Recruiter"))
):

    company = get_company(current_user["user_id"])

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    return company


# ==========================================
# UPDATE COMPANY
# ==========================================

@router.put("/company")
def edit_company(
    data: CompanyUpdate,
    current_user: dict = Depends(require_role("Recruiter"))
):

    updated = update_company(
        current_user["user_id"],
        data
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    return {
        "message": "Company updated successfully."
    }


# ==========================================
# VIEW RECRUITER PROFILE
# ==========================================

@router.get("/me")
def view_recruiter_profile(
    current_user: dict = Depends(require_role("Recruiter"))
):

    profile = get_recruiter_profile(
        current_user["user_id"]
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Recruiter profile not found."
        )

    return profile


# ==========================================
# UPDATE RECRUITER PROFILE
# ==========================================

@router.put("/me")
def edit_recruiter_profile(
    data: RecruiterUpdate,
    current_user: dict = Depends(require_role("Recruiter"))
):

    updated = update_recruiter_profile(
        current_user["user_id"],
        data.designation
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Recruiter profile not found."
        )

    return {
        "message": "Recruiter profile updated successfully."
    }
