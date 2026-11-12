from app.db.neo4j import driver


def get_graph_skill_gap_analysis(student_id, internship_id):

    query = """
    MATCH (student:Student {student_id: $student_id})
    MATCH (internship:Internship {internship_id: $internship_id})

    OPTIONAL MATCH (internship)-[req:REQUIRES_SKILL]->(skill:Skill)

    OPTIONAL MATCH (student)-[has:HAS_SKILL]->(skill)

    OPTIONAL MATCH (student)-[:COMPLETED]->(project:Project)
                    -[:USES_SKILL]->(skill)

    WITH
        internship,
        skill,
        req,
        has,
        count(DISTINCT project) AS related_projects

    WHERE skill IS NOT NULL

    RETURN
        skill.skill_id AS skill_id,
        skill.name AS skill_name,
        skill.category AS category,
        req.requirement_type AS requirement_type,
        req.minimum_proficiency AS required_proficiency,
        req.importance_weight AS importance_weight,
        coalesce(has.proficiency_level, 0) AS current_proficiency,
        related_projects

    ORDER BY skill.name
    """

    with driver.session() as session:

        result = session.run(
            query,
            student_id=student_id,
            internship_id=internship_id
        )

        rows = list(result)

    if not rows:
        return None

    skill_gaps = []
    mastered_skills = []

    total_weight = 0.0
    achieved_weight = 0.0

    for record in rows:

        current = float(record["current_proficiency"] or 0)
        required = float(record["required_proficiency"] or 0)
        weight = float(record["importance_weight"] or 1)

        gap = max(0, required - current)

        total_weight += weight

        if required > 0:
            achieved_weight += weight * min(current / required, 1)

        skill_data = {
            "skill_id": record["skill_id"],
            "skill_name": record["skill_name"],
            "category": record["category"],
            "requirement_type": record["requirement_type"],
            "current_proficiency": current,
            "required_proficiency": required,
            "proficiency_gap": round(gap, 2),
            "importance_weight": weight,
            "related_projects": record["related_projects"]
        }

        if gap > 0:
            skill_data["status"] = (
                "Missing" if current == 0 else "Needs Improvement"
            )
            skill_gaps.append(skill_data)

        else:
            skill_data["status"] = "Satisfied"
            mastered_skills.append(skill_data)

    readiness = (
        achieved_weight / total_weight * 100
        if total_weight > 0 else 100.0
    )

    return {
        "internship_id": internship_id,
        "total_required_skills": len(rows),
        "mastered_skills": len(mastered_skills),
        "missing_or_underdeveloped_skills": len(skill_gaps),
        "readiness_percentage": round(readiness, 2),
        "mastered_skills_details": mastered_skills,
        "skill_gaps": skill_gaps
    }
