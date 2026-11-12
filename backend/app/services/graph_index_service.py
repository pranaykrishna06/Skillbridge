from app.db.neo4j import driver


def create_graph_indexes():

    queries = [

        """
        CREATE INDEX student_id_index IF NOT EXISTS
        FOR (s:Student)
        ON (s.student_id)
        """,

        """
        CREATE INDEX company_id_index IF NOT EXISTS
        FOR (c:Company)
        ON (c.company_id)
        """,

        """
        CREATE INDEX skill_id_index IF NOT EXISTS
        FOR (s:Skill)
        ON (s.skill_id)
        """,

        """
        CREATE INDEX project_id_index IF NOT EXISTS
        FOR (p:Project)
        ON (p.project_id)
        """,

        """
        CREATE INDEX internship_id_index IF NOT EXISTS
        FOR (i:Internship)
        ON (i.internship_id)
        """

    ]

    with driver.session() as session:

        for query in queries:
            session.run(query)

    return {
        "status": "success",
        "message": "Neo4j indexes created successfully.",
        "total_indexes": len(queries)
    }
