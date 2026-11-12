"""
SkillBridge - Graph-Based Skill Recommendation Engine

Uses Neo4j graph relationships to recommend skills that
students should learn to improve their internship readiness.

Factors:
1. Internship demand
2. Student proficiency gap
3. Internship skill importance
4. Student project relevance
"""

from app.db.neo4j import driver


def get_graph_skill_recommendations(student_id, limit=10):
    """
    Generate personalized skill recommendations using Neo4j.

    Parameters:
        student_id (int): Authenticated student's ID.
        limit (int): Maximum number of recommendations.

    Returns:
        list: Ranked skill recommendations with explanations.
    """

    query = """
    MATCH (student:Student {student_id: $student_id})

    // Retrieve skills already possessed by the student

    OPTIONAL MATCH (student)-[has:HAS_SKILL]->(owned:Skill)

    WITH student,
         collect(
             CASE
                 WHEN owned IS NULL THEN null
                 ELSE {
                     skill_id: owned.skill_id,
                     proficiency: has.proficiency_level
                 }
             END
         ) AS owned_skills

    // Find skills required by open internships

    MATCH (internship:Internship)-[req:REQUIRES_SKILL]->(skill:Skill)

    WHERE internship.status = 'Open'
      AND date(internship.application_deadline) >= date()

    // Aggregate internship demand for each skill

    WITH
        student,
        owned_skills,
        skill,

        collect(DISTINCT {
            internship_id: internship.internship_id,
            title: internship.title,
            requirement_type: req.requirement_type
        }) AS internship_data,

        max(toFloat(coalesce(req.minimum_proficiency, 0)))
            AS required_proficiency,

        avg(toFloat(coalesce(req.importance_weight, 1.0)))
            AS average_importance

    // Find completed projects that use the recommended skill

    OPTIONAL MATCH
        (student)-[:COMPLETED]->(project:Project)
        -[:USES_SKILL]->(skill)

    WITH
        skill,
        owned_skills,
        internship_data,
        required_proficiency,
        average_importance,
        count(DISTINCT project) AS related_projects

    // Retrieve current student proficiency

    WITH
        skill,
        internship_data,
        required_proficiency,
        average_importance,
        related_projects,

        reduce(
            current = 0.0,
            item IN owned_skills |

            CASE
                WHEN item.skill_id = skill.skill_id
                THEN toFloat(coalesce(item.proficiency, 0))
                ELSE current
            END
        ) AS current_proficiency

    // Recommend only skills that need improvement

    WHERE current_proficiency < required_proficiency

    RETURN
        skill.skill_id AS skill_id,
        skill.name AS skill_name,
        skill.category AS category,

        current_proficiency,
        required_proficiency,

        required_proficiency - current_proficiency
            AS proficiency_gap,

        size(internship_data) AS internship_demand,

        related_projects,

        average_importance,

        [item IN internship_data | item.title]
            AS related_internships,

        [item IN internship_data | item.requirement_type]
            AS requirement_types

    ORDER BY
        internship_demand DESC,
        average_importance DESC,
        proficiency_gap DESC

    LIMIT $limit
    """

    with driver.session() as session:

        result = session.run(
            query,
            student_id=student_id,
            limit=limit
        )

        records = list(result)

    recommendations = []

    for record in records:

        # Retrieve graph metrics

        demand = record["internship_demand"]

        current = float(
            record["current_proficiency"] or 0
        )

        required = float(
            record["required_proficiency"] or 0
        )

        gap = float(
            record["proficiency_gap"] or 0
        )

        importance = float(
            record["average_importance"] or 1
        )

        projects = record["related_projects"]

        # ------------------------------------------------
        # 1. INTERNSHIP DEMAND SCORE
        # ------------------------------------------------

        demand_score = min(
            100.0,
            demand * 20
        )

        # ------------------------------------------------
        # 2. PROFICIENCY GAP SCORE
        # Assumes proficiency levels are on a 1-5 scale.
        # ------------------------------------------------

        gap_score = min(
            100.0,
            gap * 25
        )

        # ------------------------------------------------
        # 3. IMPORTANCE SCORE
        # ------------------------------------------------

        importance_score = min(
            100.0,
            importance * 25
        )

        # ------------------------------------------------
        # 4. PROJECT RELEVANCE SCORE
        # ------------------------------------------------

        project_score = min(
            100.0,
            projects * 25
        )

        # ------------------------------------------------
        # 5. FINAL PRIORITY SCORE
        # ------------------------------------------------

        priority_score = (
            demand_score * 0.35
            + gap_score * 0.30
            + importance_score * 0.20
            + project_score * 0.15
        )

        # ------------------------------------------------
        # 6. PRIORITY CLASSIFICATION
        # ------------------------------------------------

        if priority_score >= 70:

            priority = "High"

        elif priority_score >= 40:

            priority = "Medium"

        else:

            priority = "Low"

        # ------------------------------------------------
        # 7. EXPLANATION GENERATION
        # ------------------------------------------------

        skill_name = record["skill_name"]

        explanation = (
            f"{skill_name} is required by {demand} open internships. "
            f"Your current proficiency is {current}, while the "
            f"required proficiency is {required}. "
            f"Your proficiency gap is {gap}."
        )

        if projects > 0:

            explanation += (
                f" This skill is also connected to "
                f"{projects} of your completed projects."
            )

        # ------------------------------------------------
        # 8. BUILD RECOMMENDATION
        # ------------------------------------------------

        recommendations.append({

            "skill_id": record["skill_id"],

            "skill_name": skill_name,

            "category": record["category"],

            "current_proficiency": current,

            "required_proficiency": required,

            "proficiency_gap": gap,

            "internship_demand": demand,

            "related_projects": projects,

            "related_internships": record["related_internships"],

            "requirement_types": record["requirement_types"],

            "importance_weight": round(importance, 2),

            "priority_score": round(priority_score, 2),

            "priority": priority,

            "score_breakdown": {

                "internship_demand_score": round(
                    demand_score, 2
                ),

                "proficiency_gap_score": round(
                    gap_score, 2
                ),

                "importance_score": round(
                    importance_score, 2
                ),

                "project_relevance_score": round(
                    project_score, 2
                )

            },

            "explanation": explanation

        })

    return recommendations