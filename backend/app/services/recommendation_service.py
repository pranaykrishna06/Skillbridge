from app.db.postgres import get_postgres_connection

from app.services.recommendation_quality_service import (
    rank_recommendations
)


# ============================================================
# RECOMMENDATION WEIGHTS
# ============================================================

SKILL_WEIGHT = 0.45
ACADEMIC_WEIGHT = 0.25
PREFERENCE_WEIGHT = 0.15
SEMANTIC_WEIGHT = 0.15


# ============================================================
# SCORE NORMALIZATION
# ============================================================

def normalize_score(score):
    """
    Ensure scores remain between 0 and 100.
    """

    try:
        score = float(score or 0)
    except (TypeError, ValueError):
        return 0.0

    return round(max(0.0, min(100.0, score)), 2)


# ============================================================
# PREFERENCE MATCHING
# ============================================================

def calculate_preference_match(preferences, internship):
    """
    Calculate preference compatibility.

    Only configured preferences are evaluated.
    If no preferences are configured, return a neutral score of 100.
    """

    if not preferences:
        return 100.0, [
            "No preferences configured; neutral score applied."
        ]

    scores = []
    explanations = []

    (
        preferred_domain,
        preferred_location,
        preferred_work_mode,
        minimum_stipend,
        preferred_duration
    ) = preferences

    (
        title,
        description,
        industry,
        location,
        work_mode,
        stipend,
        duration
    ) = internship

    # Domain preference
    if preferred_domain:

        matches = (
            preferred_domain.lower() in (industry or "").lower()
            or preferred_domain.lower() in (title or "").lower()
            or preferred_domain.lower() in (description or "").lower()
        )

        scores.append(100 if matches else 0)

        explanations.append(
            f"Domain preference: "
            f"{'matched' if matches else 'not matched'}."
        )

    # Location preference
    if preferred_location:

        matches = (
            preferred_location.lower() in (location or "").lower()
        )

        scores.append(100 if matches else 0)

        explanations.append(
            f"Location preference: "
            f"{'matched' if matches else 'not matched'}."
        )

    # Work mode preference
    if preferred_work_mode:

        matches = (
            preferred_work_mode.lower()
            == (work_mode or "").lower()
        )

        scores.append(100 if matches else 0)

        explanations.append(
            f"Work mode preference: "
            f"{'matched' if matches else 'not matched'}."
        )

    # Minimum stipend preference
    if minimum_stipend is not None:

        matches = (
            float(stipend or 0) >= float(minimum_stipend)
        )

        scores.append(100 if matches else 0)

        explanations.append(
            f"Minimum stipend preference: "
            f"{'matched' if matches else 'not matched'}."
        )

    # Preferred duration
    if preferred_duration is not None:

        matches = (
            int(duration or 0) >= int(preferred_duration)
        )

        scores.append(100 if matches else 0)

        explanations.append(
            f"Preferred duration: "
            f"{'matched' if matches else 'not matched'}."
        )

    # No configured preferences
    if not scores:

        return 100.0, [
            "No preferences configured; neutral score applied."
        ]

    return round(sum(scores) / len(scores), 2), explanations


# ============================================================
# SKILL GAP RETRIEVAL
# ============================================================

def get_skill_gaps(cursor, student_id, internship_id):
    """
    Retrieve missing and underdeveloped skills
    for a particular student and internship.
    """

    cursor.execute(
        """
        SELECT
            skill_name,
            required_proficiency,
            student_proficiency,
            requirement_type,
            proficiency_gap
        FROM get_student_skill_gaps(%s, %s)
        """,
        (student_id, internship_id)
    )

    rows = cursor.fetchall()

    return [
        {
            "skill_name": row[0],
            "required_proficiency": row[1],
            "student_proficiency": row[2],
            "requirement_type": row[3],
            "proficiency_gap": row[4]
        }
        for row in rows
    ]


# ============================================================
# STUDENT INTERNSHIP RECOMMENDATIONS
# ============================================================

def get_student_recommendations(student_id, limit=10):
    """
    Generate explainable internship recommendations
    using:

    1. Skill matching
    2. Academic eligibility
    3. Student preferences
    4. Semantic similarity using pgvector

    Academic eligibility is a mandatory filter.

    Recommendation formula:

    MatchScore =
        0.45 * Skill Match
        + 0.25 * Academic Match
        + 0.15 * Preference Match
        + 0.15 * Semantic Similarity
    """

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------------
            # STEP 1: CHECK STUDENT PROFILE
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE student_id = %s
                """,
                (student_id,)
            )

            if not cursor.fetchone():

                raise ValueError(
                    "Student profile not found."
                )

            # ------------------------------------------------
            # STEP 2: RETRIEVE STUDENT EMBEDDING
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT embedding
                FROM student_embeddings
                WHERE student_id = %s
                """,
                (student_id,)
            )

            embedding_result = cursor.fetchone()

            if not embedding_result:

                raise ValueError(
                    "Student embedding not found. "
                    "Generate it first."
                )

            student_embedding = embedding_result[0]

            # ------------------------------------------------
            # STEP 3: RETRIEVE STUDENT PREFERENCES
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    preferred_domain,
                    preferred_location,
                    preferred_work_mode,
                    minimum_stipend,
                    preferred_duration
                FROM student_preferences
                WHERE student_id = %s
                """,
                (student_id,)
            )

            preferences = cursor.fetchone()

            # ------------------------------------------------
            # STEP 4: RETRIEVE OPEN INTERNSHIPS
            # AND SEMANTIC SIMILARITY
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    i.internship_id,
                    i.title,
                    i.description,
                    c.company_name,
                    c.industry,
                    i.location,
                    i.work_mode,
                    i.stipend,
                    i.duration_months,

                    1 - (
                        ie.embedding <=> %s::vector
                    ) AS semantic_similarity

                FROM internships i

                JOIN companies c
                    ON c.company_id = i.company_id

                JOIN internship_embeddings ie
                    ON ie.internship_id = i.internship_id

                WHERE i.status = 'Open'
                  AND i.application_deadline >= CURRENT_DATE

                ORDER BY ie.embedding <=> %s::vector
                """,
                (
                    str(student_embedding),
                    str(student_embedding)
                )
            )

            internships = cursor.fetchall()

            recommendations = []

            # ------------------------------------------------
            # STEP 5: PROCESS EACH INTERNSHIP
            # ------------------------------------------------

            for internship in internships:

                (
                    internship_id,
                    title,
                    description,
                    company,
                    industry,
                    location,
                    work_mode,
                    stipend,
                    duration,
                    semantic_similarity
                ) = internship

                # --------------------------------------------
                # STEP 5A: ACADEMIC ELIGIBILITY
                # --------------------------------------------

                cursor.execute(
                    """
                    SELECT is_student_eligible(%s, %s)
                    """,
                    (student_id, internship_id)
                )

                eligibility_result = cursor.fetchone()

                eligible = (
                    bool(eligibility_result[0])
                    if eligibility_result
                    and eligibility_result[0] is not None
                    else False
                )

                # Academic eligibility is mandatory.
                # Ineligible internships are excluded.

                if not eligible:
                    continue

                # --------------------------------------------
                # STEP 5B: SKILL MATCH
                # --------------------------------------------

                cursor.execute(
                    """
                    SELECT calculate_skill_match(%s, %s)
                    """,
                    (student_id, internship_id)
                )

                skill_result = cursor.fetchone()

                skill_match = normalize_score(
                    skill_result[0] if skill_result else 0
                )

                # --------------------------------------------
                # STEP 5C: ACADEMIC SCORE
                # --------------------------------------------

                # Students reaching this point have passed
                # the mandatory academic eligibility check.

                academic_match = 100.0

                # --------------------------------------------
                # STEP 5D: PREFERENCE MATCH
                # --------------------------------------------

                preference_match, preference_explanations = (
                    calculate_preference_match(
                        preferences,
                        (
                            title,
                            description,
                            industry,
                            location,
                            work_mode,
                            stipend,
                            duration
                        )
                    )
                )

                preference_match = normalize_score(
                    preference_match
                )

                # --------------------------------------------
                # STEP 5E: SEMANTIC SIMILARITY
                # --------------------------------------------

                semantic_score = normalize_score(
                    float(semantic_similarity or 0) * 100
                )

                # --------------------------------------------
                # STEP 5F: FINAL WEIGHTED SCORE
                # --------------------------------------------

                final_score = (
                    skill_match * SKILL_WEIGHT
                    + academic_match * ACADEMIC_WEIGHT
                    + preference_match * PREFERENCE_WEIGHT
                    + semantic_score * SEMANTIC_WEIGHT
                )

                final_score = normalize_score(final_score)

                # --------------------------------------------
                # STEP 5G: IDENTIFY SKILL GAPS
                # --------------------------------------------

                missing_skills = get_skill_gaps(
                    cursor,
                    student_id,
                    internship_id
                )

                # --------------------------------------------
                # STEP 5H: GENERATE EXPLANATIONS
                # --------------------------------------------

                explanations = [

                    f"Skill compatibility: {skill_match}%.",

                    "Academic eligibility requirements satisfied.",

                    f"Semantic similarity: {semantic_score}%."

                ]

                explanations.extend(
                    preference_explanations
                )

                if missing_skills:

                    skill_names = [
                        skill["skill_name"]
                        for skill in missing_skills
                    ]

                    explanations.append(
                        "Skills to improve: "
                        + ", ".join(skill_names)
                        + "."
                    )

                else:

                    explanations.append(
                        "All internship skill requirements are satisfied."
                    )

                # --------------------------------------------
                # STEP 5I: ADD RECOMMENDATION
                # --------------------------------------------

                recommendations.append(
                    {
                        "internship_id": internship_id,

                        "title": title,

                        "company": company,

                        "match_score": final_score,

                        "eligible": eligible,

                        "breakdown": {

                            "skill_match": skill_match,

                            "academic_match": academic_match,

                            "preference_match": preference_match,

                            "semantic_similarity": semantic_score

                        },

                        "missing_skills": missing_skills,

                        "explanations": explanations
                    }
                )

            # ------------------------------------------------
            # STEP 6: RECOMMENDATION QUALITY IMPROVEMENTS
            # ------------------------------------------------

            # Normalize scores, classify matches,
            # calculate confidence, prioritize skill gaps,
            # remove duplicate internships and rank results.

            recommendations = rank_recommendations(
                recommendations
            )

            # ------------------------------------------------
            # STEP 7: RETURN TOP RECOMMENDATIONS
            # ------------------------------------------------

            return recommendations[:limit]

    finally:

        connection.close()