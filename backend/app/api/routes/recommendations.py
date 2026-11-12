from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.dependencies import require_role
from app.db.postgres import get_postgres_connection

from app.services.student_service import get_student_profile

from app.services.recommendation_service import (
    get_student_recommendations,
    get_skill_gaps
)

from app.services.embedding_db_service import (
    generate_student_embedding
)

from app.services.graph_recommendation_service import (
    get_graph_skill_recommendations
)

from app.services.graph_skill_gap_service import (
    get_graph_skill_gap_analysis
)

from app.services.explainability_service import (
    generate_recommendation_explanation
)

from app.services.learning_roadmap_service import (
    get_learning_roadmap
)

from app.services.readiness_service import (
    get_internship_readiness
)

from app.services.learning_progress_service import (
    update_learning_progress,
    get_student_learning_progress,
    get_learning_progress_summary
)

from app.services.learning_resource_service import (
    generate_learning_resources
)

# Unified synchronization status services
from app.services.learning_sync_service import (
    get_learning_sync_status,
    get_student_data_sync_status
)


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


# ============================================================
# LEARNING PROGRESS REQUEST MODEL
# ============================================================

class LearningProgressRequest(BaseModel):

    progress_status: str = Field(
        ...,
        description="Not Started, In Progress or Completed"
    )

    notes: str | None = None

    proficiency_level: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Assessed proficiency level between 1 and 5"
    )


# ============================================================
# COMMON AUTHENTICATION HELPER
# ============================================================

def get_authenticated_student(current_user: dict):

    profile = get_student_profile(
        current_user["user_id"]
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found."
        )

    student_id = profile["student_id"]

    if student_id is None:

        raise HTTPException(
            status_code=500,
            detail="Unable to identify the student profile."
        )

    return student_id


# ============================================================
# 1. PERSONALIZED INTERNSHIP RECOMMENDATIONS
# ============================================================

@router.get("/")
def get_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        recommendations = get_student_recommendations(
            student_id=student_id,
            limit=limit
        )

        return {
            "message": "Recommendations generated successfully.",
            "student_id": student_id,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ============================================================
# 2. REFRESH STUDENT EMBEDDING
# ============================================================

@router.post("/refresh")
def refresh_student_embedding(
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        embedding = generate_student_embedding(student_id)

        return {
            "message": "Student embedding refreshed successfully.",
            "student_id": student_id,
            "embedding_dimensions": len(embedding),
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ============================================================
# 3. GRAPH-BASED SKILL RECOMMENDATIONS
# ============================================================

@router.get("/graph/skills")
def get_graph_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        recommendations = get_graph_skill_recommendations(
            student_id=student_id,
            limit=limit
        )

        return {
            "message": "Graph-based skill recommendations generated successfully.",
            "student_id": student_id,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating graph recommendations."
        )


# ============================================================
# 4. GRAPH-BASED SKILL GAP ANALYSIS
# ============================================================

@router.get("/graph/skill-gaps/{internship_id}")
def get_graph_skill_gaps(
    internship_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        analysis = get_graph_skill_gap_analysis(
            student_id=student_id,
            internship_id=internship_id
        )

        if analysis is None:

            raise HTTPException(
                status_code=404,
                detail="Student, internship, or skill requirements not found."
            )

        return {
            "message": "Graph-based skill gap analysis generated successfully.",
            "student_id": student_id,
            "analysis": analysis
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating graph skill gap analysis."
        )


# ============================================================
# 5. PERSONALIZED LEARNING ROADMAP
# ============================================================

@router.get("/learning-roadmap")
def generate_learning_roadmap(
    limit: int = Query(default=20, ge=1, le=50),
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        roadmap = get_learning_roadmap(
            student_id=student_id,
            limit=limit
        )

        return {
            "message": "Learning roadmap retrieved successfully.",
            "student_id": student_id,
            "learning_roadmap": roadmap
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating the learning roadmap."
        )


# ============================================================
# 6. INTERNSHIP READINESS ASSESSMENT
# ============================================================

@router.get("/readiness/{internship_id}")
def get_readiness_prediction(
    internship_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        readiness = get_internship_readiness(
            student_id=student_id,
            internship_id=internship_id
        )

        if readiness is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Internship recommendation not found. "
                    "The internship may be unavailable or "
                    "the student may not meet its eligibility requirements."
                )
            )

        return {
            "message": "Internship readiness assessment generated successfully.",
            "student_id": student_id,
            "readiness_assessment": readiness
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while calculating internship readiness."
        )


# ============================================================
# 7. UPDATE LEARNING PROGRESS
# ============================================================

@router.put("/learning-progress/{skill_id}")
def update_student_learning_progress(
    skill_id: int,
    request: LearningProgressRequest,
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        progress = update_learning_progress(
            student_id=student_id,
            skill_id=skill_id,
            progress_status=request.progress_status,
            notes=request.notes,
            proficiency_level=request.proficiency_level
        )

        return {
            "message": "Learning progress updated successfully.",
            "progress": progress
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to update learning progress."
        )


# ============================================================
# 8. GET STUDENT LEARNING PROGRESS
# ============================================================

@router.get("/learning-progress")
def get_student_progress(
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        progress = get_student_learning_progress(student_id)

        return {
            "message": "Learning progress retrieved successfully.",
            "student_id": student_id,
            "total_records": len(progress),
            "progress": progress
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve learning progress."
        )


# ============================================================
# 9. GET LEARNING PROGRESS SUMMARY
# ============================================================

@router.get("/learning-progress/summary")
def get_student_progress_summary(
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        summary = get_learning_progress_summary(student_id)

        return {
            "message": "Learning progress summary retrieved successfully.",
            "summary": summary
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve learning progress summary."
        )


# ============================================================
# 10. LEARNING RESOURCE RECOMMENDATIONS
# ============================================================

@router.get("/learning-resources")
def get_learning_resources(
    skill_name: str = Query(
        ...,
        min_length=1,
        max_length=100
    ),

    learning_stage: str = Query(
        default="Foundation"
    ),

    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        valid_stages = [
            "Foundation",
            "Improvement",
            "Completed"
        ]

        if learning_stage not in valid_stages:

            raise ValueError(
                "Invalid learning stage. "
                "Choose Foundation, Improvement or Completed."
            )

        resources = generate_learning_resources(
            skill_name=skill_name,
            learning_stage=learning_stage
        )

        return {
            "message": "Learning resources generated successfully.",
            "student_id": student_id,
            "learning_resources": resources
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to generate learning resources."
        )


# ============================================================
# 11. UNIFIED LEARNING SYNCHRONIZATION STATUS
# ============================================================

@router.get("/learning-sync-status")
def get_student_learning_sync_status(
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        # Learning progress, skill additions and deletions
        learning_sync_history = get_learning_sync_status(
            student_id
        )

        # Student profile and project modifications
        student_data_sync_history = get_student_data_sync_status(
            student_id
        )

        return {
            "message": "Synchronization status retrieved successfully.",

            "student_id": student_id,

            "learning_skill_synchronization": {
                "total_records": len(learning_sync_history),
                "records": learning_sync_history
            },

            "profile_project_synchronization": {
                "total_records": len(student_data_sync_history),
                "records": student_data_sync_history
            },

            "total_synchronization_events": (
                len(learning_sync_history)
                + len(student_data_sync_history)
            )
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve synchronization status."
        )


# ============================================================
# 12. INTERNSHIP SKILL GAP ANALYSIS (POSTGRESQL)
# ============================================================

@router.get("/{internship_id}/skill-gaps")
def get_internship_skill_gaps(
    internship_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT internship_id
                FROM internships
                WHERE internship_id = %s
                """,
                (internship_id,)
            )

            if not cursor.fetchone():

                raise HTTPException(
                    status_code=404,
                    detail="Internship not found."
                )

            skill_gaps = get_skill_gaps(
                cursor,
                student_id,
                internship_id
            )

            return {
                "message": "Skill gap analysis retrieved successfully.",
                "student_id": student_id,
                "internship_id": internship_id,
                "total_skill_gaps": len(skill_gaps),
                "skill_gaps": skill_gaps
            }

    except HTTPException:
        raise

    finally:

        connection.close()


# ============================================================
# 13. EXPLAINABLE INTERNSHIP RECOMMENDATION
# ============================================================

@router.get("/{internship_id}/explanation")
def get_recommendation_explanation(
    internship_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        recommendations = get_student_recommendations(
            student_id=student_id,
            limit=50
        )

        recommendation = next(
            (
                item for item in recommendations
                if item["internship_id"] == internship_id
            ),
            None
        )

        if not recommendation:

            raise HTTPException(
                status_code=404,
                detail="Internship recommendation not found or student is not eligible."
            )

        explanation = generate_recommendation_explanation(
            recommendation
        )

        return {
            "message": "Recommendation explanation generated successfully.",
            "student_id": student_id,
            "explanation": explanation
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating the explanation."
        )


# ============================================================
# 14. DETAILED INTERNSHIP RECOMMENDATION
# ============================================================

@router.get("/{internship_id}")
def get_detailed_recommendation(
    internship_id: int,
    current_user: dict = Depends(require_role("Student"))
):

    student_id = get_authenticated_student(current_user)

    try:

        recommendations = get_student_recommendations(
            student_id=student_id,
            limit=50
        )

        recommendation = next(
            (
                item for item in recommendations
                if item["internship_id"] == internship_id
            ),
            None
        )

        if not recommendation:

            raise HTTPException(
                status_code=404,
                detail="Internship unavailable or not eligible."
            )

        return {
            "message": "Detailed recommendation retrieved successfully.",
            "student_id": student_id,
            "recommendation": recommendation
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while retrieving the recommendation."
        )