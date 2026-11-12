from app.services.recommendation_service import (
    get_student_recommendations
)


# ============================================================
# HELPER: GET SCORE FROM AVAILABLE FIELDS
# ============================================================

def get_score(data, possible_keys):

    for key in possible_keys:

        value = data.get(key)

        if value is not None:

            try:
                return float(value)
            except (ValueError, TypeError):
                continue

    return 0.0


# ============================================================
# INTERNSHIP READINESS SERVICE
# ============================================================

def get_internship_readiness(student_id: int, internship_id: int):

    recommendations = get_student_recommendations(
        student_id=student_id,
        limit=50
    )

    recommendation = next(
        (
            item for item in recommendations
            if item.get("internship_id") == internship_id
        ),
        None
    )

    if recommendation is None:
        return None

    breakdown = recommendation.get(
        "score_breakdown",
        {}
    )

    if not isinstance(breakdown, dict):
        breakdown = {}

    # --------------------------------------------------------
    # EXTRACT EXISTING RECOMMENDATION SCORES
    # --------------------------------------------------------

    skill_score = get_score(
        breakdown,
        ["skill_match", "skill_score", "skills"]
    )

    academic_score = get_score(
        breakdown,
        ["academic", "academic_score"]
    )

    preference_score = get_score(
        breakdown,
        ["preference", "preference_score"]
    )

    semantic_score = get_score(
        breakdown,
        ["semantic", "semantic_score"]
    )

    overall_score = get_score(
        recommendation,
        [
            "overall_score",
            "match_score",
            "final_score",
            "score"
        ]
    )

    # Use the recommendation's overall score as the
    # readiness score to maintain consistency.
    readiness_score = round(
        max(0, min(100, overall_score)),
        2
    )

    # --------------------------------------------------------
    # ACADEMIC ELIGIBILITY
    # --------------------------------------------------------

    academically_eligible = recommendation.get(
        "eligible",
        True
    )

    if not academically_eligible:

        readiness_status = "Not Eligible"

    elif readiness_score >= 80:

        readiness_status = "Highly Ready"

    elif readiness_score >= 65:

        readiness_status = "Ready"

    elif readiness_score >= 45:

        readiness_status = "Moderately Ready"

    else:

        readiness_status = "Needs Improvement"

    # --------------------------------------------------------
    # SKILL GAP INFORMATION
    # --------------------------------------------------------

    skill_gaps = recommendation.get(
        "skill_gaps",
        []
    )

    missing_skills = []

    if isinstance(skill_gaps, list):

        for gap in skill_gaps:

            if isinstance(gap, dict):

                missing_skills.append({
                    "skill_name": gap.get(
                        "skill_name",
                        gap.get("name", "Unknown")
                    ),
                    "required_proficiency": gap.get(
                        "required_proficiency",
                        gap.get("minimum_proficiency", 0)
                    ),
                    "current_proficiency": gap.get(
                        "current_proficiency",
                        gap.get("student_proficiency", 0)
                    ),
                    "proficiency_gap": gap.get(
                        "proficiency_gap",
                        gap.get("gap", 0)
                    )
                })

            elif isinstance(gap, str):

                missing_skills.append({
                    "skill_name": gap
                })

    # --------------------------------------------------------
    # PROJECT EXPERIENCE
    # --------------------------------------------------------

    projects = recommendation.get(
        "projects",
        recommendation.get("related_projects", [])
    )

    if isinstance(projects, list):
        project_count = len(projects)
    else:
        project_count = 0

    # --------------------------------------------------------
    # READINESS RECOMMENDATIONS
    # --------------------------------------------------------

    improvement_suggestions = []

    if skill_score < 60:

        improvement_suggestions.append(
            "Improve your proficiency in the internship's required skills."
        )

    if preference_score < 60:

        improvement_suggestions.append(
            "Review your internship preferences and consider expanding them."
        )

    if semantic_score < 60:

        improvement_suggestions.append(
            "Improve your profile and project descriptions with relevant technical details."
        )

    if project_count == 0:

        improvement_suggestions.append(
            "Add relevant projects to demonstrate practical experience."
        )

    if missing_skills:

        improvement_suggestions.append(
            "Prioritize learning the missing skills identified in the skill gap analysis."
        )

    if not improvement_suggestions:

        improvement_suggestions.append(
            "Maintain your current preparation and continue developing practical experience."
        )

    # --------------------------------------------------------
    # READINESS RESULT
    # --------------------------------------------------------

    return {

        "student_id": student_id,

        "internship_id": internship_id,

        "internship_title": recommendation.get(
            "internship_title",
            recommendation.get("title")
        ),

        "company_name": recommendation.get(
            "company_name"
        ),

        "readiness_score": readiness_score,

        "readiness_status": readiness_status,

        "academic_eligibility": academically_eligible,

        "score_breakdown": {

            "skill_match": skill_score,

            "academic_score": academic_score,

            "preference_match": preference_score,

            "semantic_similarity": semantic_score

        },

        "skill_gap_count": len(missing_skills),

        "missing_skills": missing_skills,

        "project_count": project_count,

        "improvement_suggestions": improvement_suggestions,

        "explanation": (
            f"The student's internship readiness score is "
            f"{readiness_score}%. The assessment uses the existing "
            f"internship recommendation score and academic eligibility."
        )

    }