from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_role

from app.schemas.student import (
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentSkillCreate,
    StudentProjectCreate
)

from app.services.student_service import (
    create_student_profile,
    get_student_profile,
    update_student_profile,
    get_student_skills,
    add_student_skill,
    delete_student_skill,
    get_student_projects,
    add_student_project,
    delete_student_project
)


router = APIRouter(
    prefix="/api/students",
    tags=["Student"]
)


# ==========================================
# STUDENT PROFILE
# ==========================================

@router.post("/profile", status_code=status.HTTP_201_CREATED)
def create_profile(
    data: StudentProfileCreate,
    current_user: dict = Depends(require_role("Student"))
):

    existing = get_student_profile(current_user["user_id"])

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Student profile already exists."
        )

    try:
        create_student_profile(current_user["user_id"], data)

        return {
            "message": "Student profile created successfully."
        }

    except Exception as error:
        error_code = getattr(error, "sqlstate", None)

        if error_code == "23505":
            raise HTTPException(
                status_code=409,
                detail="Registration number already exists."
            )

        if error_code == "23503":
            raise HTTPException(
                status_code=400,
                detail="Invalid student account."
            )

        raise


@router.get("/me")
def view_profile(
    current_user: dict = Depends(require_role("Student"))
):

    profile = get_student_profile(current_user["user_id"])

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found. Create your profile first."
        )

    return profile


@router.put("/me")
def edit_profile(
    data: StudentProfileUpdate,
    current_user: dict = Depends(require_role("Student"))
):

    updated = update_student_profile(
        current_user["user_id"],
        data
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found."
        )

    return {
        "message": "Student profile updated successfully."
    }


# ==========================================
# STUDENT SKILLS
# ==========================================

@router.get("/skills")
def view_skills(
    current_user: dict = Depends(require_role("Student"))
):

    return get_student_skills(current_user["user_id"])


@router.post("/skills")
def add_skill(
    data: StudentSkillCreate,
    current_user: dict = Depends(require_role("Student"))
):

    profile = get_student_profile(current_user["user_id"])

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Create your student profile first."
        )

    try:
        add_student_skill(current_user["user_id"], data)

        return {
            "message": "Student skill added successfully."
        }

    except Exception as error:
        if getattr(error, "sqlstate", None) == "23503":
            raise HTTPException(
                status_code=404,
                detail="Student profile or skill not found."
            )
        raise


@router.delete("/skills/{skill_id}")
def remove_skill(
    skill_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    deleted = delete_student_skill(
        current_user["user_id"],
        skill_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Student skill not found."
        )

    return {
        "message": "Student skill removed successfully."
    }


# ==========================================
# STUDENT PROJECTS
# ==========================================

@router.get("/projects")
def view_projects(
    current_user: dict = Depends(require_role("Student"))
):

    return get_student_projects(current_user["user_id"])


@router.post("/projects", status_code=status.HTTP_201_CREATED)
def add_project(
    data: StudentProjectCreate,
    current_user: dict = Depends(require_role("Student"))
):

    profile = get_student_profile(current_user["user_id"])

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Create your student profile first."
        )

    if (
        data.start_date
        and data.end_date
        and data.end_date < data.start_date
    ):
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date."
        )

    project_id = add_student_project(
        current_user["user_id"],
        data
    )

    return {
        "message": "Project added successfully.",
        "project_id": project_id
    }


@router.delete("/projects/{project_id}")
def remove_project(
    project_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    deleted = delete_student_project(
        current_user["user_id"],
        project_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    return {
        "message": "Project deleted successfully."
    }
