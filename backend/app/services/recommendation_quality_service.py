def normalize_score(score):
    """
    Ensure scores are valid and remain between 0 and 100.
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return 0.0

    return round(max(0.0, min(100.0, score)), 2)


def classify_match(score):
    """
    Classify an internship based on its match score.
    """
    score = normalize_score(score)

    if score >= 85:
        return "Excellent Match"

    elif score >= 70:
        return "Good Match"

    elif score >= 50:
        return "Moderate Match"

    return "Low Match"


def calculate_recommendation_confidence(recommendation):
    """
    Estimate recommendation confidence based on the availability
    of recommendation data.

    This is a rule-based confidence indicator, not a probability.
    """

    breakdown = recommendation.get("breakdown", {})

    available_components = [
        "skill_match",
        "academic_match",
        "preference_match",
        "semantic_similarity"
    ]

    available_count = 0

    for component in available_components:
        if breakdown.get(component) is not None:
            available_count += 1

    confidence = (available_count / len(available_components)) * 100

    return round(confidence, 2)


def prioritize_skill_gaps(missing_skills):
    """
    Sort missing skills by importance and proficiency gap.
    """

    requirement_priority = {
        "Required": 3,
        "Preferred": 2,
        "Optional": 1
    }

    def priority(skill):
        requirement_type = skill.get(
            "requirement_type", "Optional"
        )

        importance = requirement_priority.get(
            requirement_type, 1
        )

        proficiency_gap = skill.get("proficiency_gap", 0)

        return importance, proficiency_gap

    return sorted(
        missing_skills or [],
        key=priority,
        reverse=True
    )


def enrich_recommendation(recommendation):
    """
    Add additional quality information without changing
    the existing recommendation fields.
    """

    recommendation = recommendation.copy()

    score = normalize_score(
        recommendation.get("match_score", 0)
    )

    recommendation["match_score"] = score

    recommendation["match_level"] = classify_match(score)

    recommendation["recommendation_confidence"] = (
        calculate_recommendation_confidence(recommendation)
    )

    recommendation["missing_skills"] = prioritize_skill_gaps(
        recommendation.get("missing_skills", [])
    )

    return recommendation


def rank_recommendations(recommendations):
    """
    Remove duplicate internships, enrich results and rank
    recommendations from highest to lowest score.
    """

    unique_recommendations = {}
    
    for recommendation in recommendations:

        internship_id = recommendation.get("internship_id")

        if internship_id is None:
            continue

        enriched = enrich_recommendation(recommendation)

        existing = unique_recommendations.get(internship_id)

        if (
            existing is None
            or enriched["match_score"] > existing["match_score"]
        ):
            unique_recommendations[internship_id] = enriched

    ranked = list(unique_recommendations.values())

    ranked.sort(
        key=lambda item: (
            item["match_score"],
            item["recommendation_confidence"]
        ),
        reverse=True
    )

    return ranked
