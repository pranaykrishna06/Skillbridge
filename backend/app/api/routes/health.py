from fastapi import APIRouter

from app.db.postgres import check_postgres_connection
from app.db.neo4j import check_neo4j_connection


router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "application": "SkillBridge",
        "status": "running"
    }


@router.get("/health/postgres")
def postgres_health():
    version = check_postgres_connection()

    return {
        "database": "PostgreSQL",
        "status": "connected",
        "version": version
    }


@router.get("/health/neo4j")
def neo4j_health():
    message = check_neo4j_connection()

    return {
        "database": "Neo4j",
        "status": "connected",
        "message": message
    }