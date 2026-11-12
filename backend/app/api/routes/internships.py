from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, require_role

from app.schemas.internship import (
    InternshipCreate,
    InternshipUpdate,
    InternshipSkillCreate
)

from app.services.internship_service import (
    create_internship,
    get_all_internships,
    get_recruiter_internships,
    get_internship,
    update_internship,
    delete_internship,
    add_internship_skill,
    get_internship_skills
)

router = APIRouter(
    prefix="/api/internships",
    tags=["Internships"]
)


# CREATE INTERNSHIP

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_internship(
    data: InternshipCreate,
    current_user: dict = Depends(require_role("Recruiter"))
):

    if data.work_mode not in ["Remote", "Hybrid", "On-site"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid work mode."
        )

    if data.application_deadline < date.today():
        raise HTTPException(
            status_code=400,
            detail="Application deadline cannot be in the past."
        )

    if data.status not in ["Draft", "Open"]:
        raise HTTPException(
            status_code=400,
            detail="New internship status must be Draft or Open."
        )

    internship_id = create_internship(
        current_user["user_id"],
        data
    )

    if not internship_id:
        raise HTTPException(
            status_code=404,
            detail="Recruiter profile not found."
        )

    return {
        "message": "Internship created successfully.",
        "internship_id": internship_id,
        "status": data.status
    }


# VIEW ALL OPEN INTERNSHIPS

@router.get("/")
def view_all_internships(
    current_user: dict = Depends(get_current_user)
):

    return get_all_internships()
# VIEW RECRUITER'S OWN INTERNSHIPS

@router.get("/my")
def view_my_internships(
    current_user: dict = Depends(require_role("Recruiter"))
):
    return get_recruiter_internships(current_user["user_id"])

# VIEW SINGLE INTERNSHIP

@router.get("/{internship_id}")
def view_internship(
    internship_id: int,
    current_user: dict = Depends(get_current_user)
):

    internship = get_internship(internship_id)

    if not internship:
        raise HTTPException(
            status_code=404,
            detail="Internship not found."
        )

    return internship


# UPDATE INTERNSHIP

@router.put("/{internship_id}")
def edit_internship(
    internship_id: int,
    data: InternshipUpdate,
    current_user: dict = Depends(require_role("Recruiter"))
):

    if data.work_mode not in ["Remote", "Hybrid", "On-site"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid work mode."
        )

    if data.status not in ["Draft", "Open", "Closed", "Expired"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid internship status."
        )

    updated = update_internship(
        current_user["user_id"],
        internship_id,
        data
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Internship not found or you do not own it."
        )

    return {
        "message": "Internship updated successfully."
    }


# DELETE INTERNSHIP

@router.delete("/{internship_id}")
def remove_internship(
    internship_id: int,
    current_user: dict = Depends(require_role("Recruiter"))
):

    deleted = delete_internship(
        current_user["user_id"],
        internship_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Internship not found or you do not own it."
        )

    return {
        "message": "Internship deleted successfully."
    }


# ADD INTERNSHIP SKILL

@router.post("/{internship_id}/skills")
def add_required_skill(
    internship_id: int,
    data: InternshipSkillCreate,
    current_user: dict = Depends(require_role("Recruiter"))
):

    internship = get_internship(internship_id)

    if not internship or internship["created_by"] != current_user["user_id"]:
        raise HTTPException(
            status_code=404,
            detail="Internship not found or you do not own it."
        )

    if data.requirement_type not in ["Mandatory", "Preferred"]:
        raise HTTPException(
            status_code=400,
            detail="Requirement type must be Mandatory or Preferred."
        )

    add_internship_skill(internship_id, data)

    return {
        "message": "Internship skill added successfully."
    }


# VIEW INTERNSHIP SKILLS

@router.get("/{internship_id}/skills")
def view_required_skills(
    internship_id: int,
    current_user: dict = Depends(get_current_user)
):

    internship = get_internship(internship_id)

    if not internship:
        raise HTTPException(
            status_code=404,
            detail="Internship not found."
        )

    return get_internship_skills(internship_id)
