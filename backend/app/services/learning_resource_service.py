from urllib.parse import quote_plus


# ============================================================
# LEARNING RESOURCE SERVICE
# ============================================================

def generate_learning_resources(
    skill_name: str,
    learning_stage: str = "Foundation"
):
    """
    Generate learning resource recommendations
    for a particular skill.

    Resources include:
    1. Video tutorials
    2. Online courses
    3. Official documentation
    4. Practical exercises
    5. GitHub projects
    """

    if not skill_name or not skill_name.strip():
        raise ValueError("Skill name is required.")

    skill_name = skill_name.strip()

    encoded_skill = quote_plus(skill_name)

    # --------------------------------------------------------
    # DETERMINE LEARNING LEVEL
    # --------------------------------------------------------

    stage_levels = {
        "Foundation": "beginner",
        "Improvement": "intermediate",
        "Completed": "advanced"
    }

    learning_level = stage_levels.get(
        learning_stage,
        "beginner"
    )

    # --------------------------------------------------------
    # GENERATE RESOURCE LINKS
    # --------------------------------------------------------

    resources = [

        {
            "resource_type": "Video Tutorial",

            "platform": "YouTube",

            "description": (
                f"Watch {learning_level}-level video tutorials "
                f"for {skill_name}."
            ),

            "url": (
                f"https://www.youtube.com/results?search_query="
                f"{encoded_skill}+{learning_level}+tutorial"
            ),

            "is_free": True
        },

        {
            "resource_type": "Online Course",

            "platform": "Coursera",

            "description": (
                f"Find structured courses covering {skill_name}."
            ),

            "url": (
                f"https://www.coursera.org/search?query="
                f"{encoded_skill}"
            ),

            "is_free": "Some courses"
        },

        {
            "resource_type": "Practical Learning",

            "platform": "freeCodeCamp",

            "description": (
                f"Find practical exercises and tutorials "
                f"related to {skill_name}."
            ),

            "url": (
                f"https://www.freecodecamp.org/news/search/"
                f"?query={encoded_skill}"
            ),

            "is_free": True
        },

        {
            "resource_type": "Documentation",

            "platform": "Google Search",

            "description": (
                f"Find official documentation and reference "
                f"materials for {skill_name}."
            ),

            "url": (
                f"https://www.google.com/search?q="
                f"{encoded_skill}+official+documentation"
            ),

            "is_free": True
        },

        {
            "resource_type": "Practical Projects",

            "platform": "GitHub",

            "description": (
                f"Explore practical projects and repositories "
                f"related to {skill_name}."
            ),

            "url": (
                f"https://github.com/search?q="
                f"{encoded_skill}&type=repositories"
            ),

            "is_free": True
        }

    ]

    # --------------------------------------------------------
    # RETURN LEARNING RESOURCES
    # --------------------------------------------------------

    return {

        "skill_name": skill_name,

        "learning_stage": learning_stage,

        "recommended_level": learning_level,

        "total_resources": len(resources),

        "resources": resources

    }