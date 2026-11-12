from neo4j import GraphDatabase

from app.core.config import settings


driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USERNAME,
        settings.NEO4J_PASSWORD
    )
)


def check_neo4j_connection():
    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run(
            "RETURN 'Neo4j Connected Successfully' AS message"
        )

        return result.single()["message"]


def close_neo4j_connection():
    driver.close()