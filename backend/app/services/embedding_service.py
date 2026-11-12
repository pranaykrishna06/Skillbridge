"""Embedding generation is intentionally disabled in this SkillBridge build.

The application continues to support normal internship, student, recruiter,
application, notification, and Neo4j graph workflows without downloading
external machine-learning models.
"""

EMBEDDING_DIMENSION = 384


def get_device() -> str:
    return "disabled"


def get_embedding_model():
    raise RuntimeError("AI recommendation embeddings are disabled in this build.")


def generate_embedding(text: str) -> list[float]:
    raise RuntimeError("AI recommendation embeddings are disabled in this build.")


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    raise RuntimeError("AI recommendation embeddings are disabled in this build.")
