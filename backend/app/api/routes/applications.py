from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import require_role

from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    StudentPreferenceUpdate
)

from app.services.application_service import (
    get_available_internships,
    apply_for_internship,
    get_student_applications,
    get_application_details,
    withdraw_application,
    get_recruiter_applications,
    update_application_status,
    get_application_history,
    save_internship,
    get_saved_internships,
    update_student_preferences
)


router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"]
)


# STUDENT: AVAILABLE INTERNSHIPS

@router.get("/available")
def available_internships(
    current_user: dict = Depends(require_role("Student"))
):
    return get_available_internships(current_user["user_id"])


# STUDENT: APPLY

@router.post("/")
def apply(
    data: ApplicationCreate,
    current_user: dict = Depends(require_role("Student"))
):
    result = apply_for_internship(current_user["user_id"], data)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "message": "Application submitted successfully.",
        **result
    }


# STUDENT: MY APPLICATIONS

@router.get("/me")
def my_applications(
    current_user: dict = Depends(require_role("Student"))
):
    return get_student_applications(current_user["user_id"])


# RECRUITER: VIEW APPLICATIONS

@router.get("/recruiter")
def recruiter_applications(
    current_user: dict = Depends(require_role("Recruiter"))
):
    return get_recruiter_applications(current_user["user_id"])


# STUDENT: VIEW SAVED INTERNSHIPS

@router.get("/saved")
def saved(
    current_user: dict = Depends(require_role("Student"))
):
    return get_saved_internships(current_user["user_id"])


# STUDENT: APPLICATION DETAILS

@router.get("/{application_id}")
def application_details(
    application_id: int,
    current_user: dict = Depends(require_role("Student"))
):
    result = get_application_details(
        application_id,
        current_user["user_id"]
    )

    if not result:
        raise HTTPException(status_code=404, detail="Application not found.")

    return result


# STUDENT: WITHDRAW

@router.put("/{application_id}/withdraw")
def withdraw(
    application_id: int,
    current_user: dict = Depends(require_role("Student"))
):
    result = withdraw_application(
        application_id,
        current_user["user_id"]
    )

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Application not found.")

    if result == "invalid_status":
        raise HTTPException(status_code=400, detail="Application cannot be withdrawn.")

    return {"message": "Application withdrawn successfully."}


# STUDENT: SAVE INTERNSHIP

@router.post("/save/{internship_id}")
def save(
    internship_id: int,
    current_user: dict = Depends(require_role("Student"))
):
    result = save_internship(current_user["user_id"], internship_id)

    if result == "profile_not_found":
        raise HTTPException(
            status_code=404,
            detail="Student profile not found. Complete your student profile before saving internships."
        )

    if result == "internship_unavailable":
        raise HTTPException(
            status_code=404,
            detail="This internship is no longer available to save."
        )

    if result == "already_saved":
        raise HTTPException(
            status_code=409,
            detail="You have already saved this internship."
        )

    return {"message": "Internship saved successfully."}


# STUDENT: UPDATE PREFERENCES

@router.put("/preferences")
def preferences(
    data: StudentPreferenceUpdate,
    current_user: dict = Depends(require_role("Student"))
):
    if data.preferred_work_mode and data.preferred_work_mode not in [
        "Remote", "Hybrid", "On-site"
    ]:
        raise HTTPException(status_code=400, detail="Invalid work mode.")

    update_student_preferences(current_user["user_id"], data)

    return {"message": "Preferences updated successfully."}


# RECRUITER: UPDATE APPLICATION STATUS

@router.put("/{application_id}/status")
def change_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    current_user: dict = Depends(require_role("Recruiter"))
):
    allowed_statuses = [
        "Under Review",
        "Shortlisted",
        "Interview",
        "Selected",
        "Rejected"
    ]

    if data.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status.")

    result = update_application_status(
        application_id,
        current_user["user_id"],
        data.status,
        data.remarks
    )

    if result is False:
        raise HTTPException(status_code=404, detail="Application not found.")

    if result == "terminal":
        raise HTTPException(status_code=400, detail="Application is already finalized.")

    if result == "same":
        raise HTTPException(status_code=400, detail="Application already has this status.")

    return {"message": "Application status updated successfully."}


# RECRUITER: STATUS HISTORY

@router.get("/{application_id}/history")
def application_history(
    application_id: int,
    current_user: dict = Depends(require_role("Recruiter"))
):
    result = get_application_history(
        application_id,
        current_user["user_id"]
    )

    return result
