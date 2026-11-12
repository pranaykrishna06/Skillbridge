from app.services.graph_recommendation_service import (
    get_graph_skill_recommendations
)

from app.services.learning_progress_service import (
    get_student_learning_progress
)

from app.services.learning_resource_service import (
    generate_learning_resources
)


# ============================================================
# LEARNING ROADMAP SERVICE
# ============================================================

def get_learning_roadmap(student_id: int, limit: int = 20):
    """
    Generate a personalized learning roadmap using
    graph-based skill recommendations.

    Skills are prioritized according to:
    1. Priority score
    2. Requirement importance
    3. Proficiency gap

    Learning progress is retrieved from PostgreSQL.

    Learning resources are generated for every skill.
    """

    if limit < 1 or limit > 50:
        raise ValueError(
            "Roadmap limit must be between 1 and 50."
        )

    # --------------------------------------------------------
    # STEP 1: GET GRAPH-BASED SKILL RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = get_graph_skill_recommendations(
        student_id=student_id,
        limit=50
    )

    # --------------------------------------------------------
    # STEP 2: RETRIEVE SAVED LEARNING PROGRESS
    # --------------------------------------------------------

    saved_progress = get_student_learning_progress(student_id)

    progress_lookup = {
        item["skill_id"]: item
        for item in saved_progress
    }

    # --------------------------------------------------------
    # HANDLE EMPTY RECOMMENDATIONS
    # --------------------------------------------------------

    if not recommendations:

        return {
            "student_id": student_id,
            "total_skills": 0,
            "foundation_skills": 0,
            "improvement_skills": 0,
            "completed_skills": 0,
            "in_progress_skills": 0,
            "not_started_skills": 0,
            "roadmap": [],
            "message": (
                "No skill gaps found. Your current skills "
                "match the requirements of the available internships."
            )
        }

    # --------------------------------------------------------
    # STEP 3: PRIORITIZE SKILLS
    # --------------------------------------------------------

    requirement_priority = {
        "required": 3,
        "preferred": 2,
        "optional": 1
    }

    def get_priority_value(skill):

        priority_score = float(
            skill.get("priority_score") or 0
        )

        requirement_types = skill.get(
            "requirement_types", []
        )

        if isinstance(requirement_types, str):
            requirement_types = [requirement_types]

        requirement_value = max(
            [
                requirement_priority.get(
                    str(item).lower(), 1
                )
                for item in requirement_types
            ],
            default=1
        )

        proficiency_gap = max(
            0,
            float(skill.get("required_proficiency") or 0)
            - float(skill.get("current_proficiency") or 0)
        )

        return (
            priority_score,
            requirement_value,
            proficiency_gap
        )

    recommendations = sorted(
        recommendations,
        key=get_priority_value,
        reverse=True
    )

    # --------------------------------------------------------
    # STEP 4: GENERATE LEARNING ROADMAP
    # --------------------------------------------------------

    roadmap = []

    for index, skill in enumerate(
        recommendations[:limit],
        start=1
    ):

        skill_name = skill.get(
            "skill_name",
            "Unknown Skill"
        )

        current_level = float(
            skill.get("current_proficiency") or 0
        )

        target_level = float(
            skill.get("required_proficiency") or 0
        )

        proficiency_gap = max(
            0,
            target_level - current_level
        )

        priority = skill.get(
            "priority",
            "Low"
        )

        skill_id = skill.get("skill_id")

        # --------------------------------------------
        # RETRIEVE SAVED PROGRESS FOR THIS SKILL
        # --------------------------------------------

        saved_record = progress_lookup.get(skill_id)

        # --------------------------------------------
        # DETERMINE LEARNING STAGE
        # --------------------------------------------

        if proficiency_gap == 0:

            learning_stage = "Completed"

            learning_steps = [
                f"Maintain your existing {skill_name} knowledge.",
                f"Apply {skill_name} in practical projects.",
                f"Explore advanced applications of {skill_name}."
            ]

        elif current_level == 0:

            learning_stage = "Foundation"

            learning_steps = [
                f"Understand the fundamentals of {skill_name}.",
                f"Learn the core concepts and terminology of {skill_name}.",
                f"Complete beginner-level exercises using {skill_name}.",
                f"Build a small practical project using {skill_name}."
            ]

        else:

            learning_stage = "Improvement"

            learning_steps = [
                f"Revise the concepts of {skill_name}.",
                f"Practice intermediate-level problems using {skill_name}.",
                f"Explore advanced concepts and practical applications.",
                f"Build a project demonstrating proficiency in {skill_name}."
            ]

        # --------------------------------------------
        # DETERMINE PROGRESS STATUS
        # --------------------------------------------

        if saved_record:

            progress_status = saved_record["progress_status"]

        elif proficiency_gap == 0:

            progress_status = "Completed"

        else:

            progress_status = "Not Started"

        # --------------------------------------------
        # STEP 2A: GENERATE LEARNING RESOURCES
        # --------------------------------------------

        learning_resources = generate_learning_resources(
            skill_name=skill_name,
            learning_stage=learning_stage
        )

        # --------------------------------------------
        # PRIORITY DESCRIPTION
        # --------------------------------------------

        requirement_types = skill.get(
            "requirement_types",
            []
        )

        if isinstance(requirement_types, str):
            requirement_types = [requirement_types]

        if any(
            str(item).lower() == "required"
            for item in requirement_types
        ):

            priority_reason = (
                "This skill is required by one or more internships."
            )

        elif any(
            str(item).lower() == "preferred"
            for item in requirement_types
        ):

            priority_reason = (
                "This skill is preferred by available internships."
            )

        else:

            priority_reason = (
                "Improving this skill may increase internship compatibility."
            )

        # --------------------------------------------
        # RELATED INTERNSHIPS
        # --------------------------------------------

        related_internships = skill.get(
            "related_internships",
            []
        )

        # --------------------------------------------
        # ADD ROADMAP ITEM
        # --------------------------------------------

        roadmap.append({

            "step": index,

            "skill_id": skill_id,

            "skill_name": skill_name,

            "category": skill.get("category"),

            "learning_stage": learning_stage,

            "priority": priority,

            "priority_score": skill.get(
                "priority_score",
                0
            ),

            "current_proficiency": current_level,

            "target_proficiency": target_level,

            "proficiency_gap": proficiency_gap,

            "progress_status": progress_status,

            "progress_notes": (
                saved_record.get("notes")
                if saved_record
                else None
            ),

            "progress_updated_at": (
                saved_record.get("updated_at")
                if saved_record
                else None
            ),

            "internship_demand": skill.get(
                "internship_demand",
                0
            ),

            "related_projects": skill.get(
                "related_projects",
                0
            ),

            "requirement_types": requirement_types,

            "related_internships": related_internships,

            "learning_steps": learning_steps,

            # Newly integrated learning resources
            "learning_resources": learning_resources,

            "priority_reason": priority_reason,

            "reason": skill.get(
                "explanation",
                "This skill is required by available internships."
            )

        })

    # --------------------------------------------------------
    # STEP 5: CALCULATE ROADMAP SUMMARY
    # --------------------------------------------------------

    foundation_count = sum(
        1 for item in roadmap
        if item["learning_stage"] == "Foundation"
    )

    improvement_count = sum(
        1 for item in roadmap
        if item["learning_stage"] == "Improvement"
    )

    completed_count = sum(
        1 for item in roadmap
        if item["progress_status"] == "Completed"
    )

    in_progress_count = sum(
        1 for item in roadmap
        if item["progress_status"] == "In Progress"
    )

    not_started_count = sum(
        1 for item in roadmap
        if item["progress_status"] == "Not Started"
    )

    # --------------------------------------------------------
    # STEP 6: RETURN LEARNING ROADMAP
    # --------------------------------------------------------

    return {

        "student_id": student_id,

        "total_skills": len(roadmap),

        "foundation_skills": foundation_count,

        "improvement_skills": improvement_count,

        "completed_skills": completed_count,

        "in_progress_skills": in_progress_count,

        "not_started_skills": not_started_count,

        "roadmap": roadmap,

        "message": (
            "Personalized learning roadmap generated successfully."
        )

    }