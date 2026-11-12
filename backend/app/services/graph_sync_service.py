from datetime import date, datetime
from decimal import Decimal

from app.db.postgres import get_postgres_connection
from app.db.neo4j import driver


# ============================================================
# 1. FETCH DATA FROM POSTGRESQL
# ============================================================

def fetch_graph_data():
    """
    Fetch all graph-related information from PostgreSQL.

    PostgreSQL is treated as the primary source of truth.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Students
            cursor.execute("""
                SELECT
                    s.student_id,
                    u.full_name,
                    u.email,
                    s.department,
                    s.year_of_study,
                    s.cgpa,
                    s.graduation_year
                FROM students s
                JOIN users u
                    ON s.student_id = u.user_id
            """)

            students = cursor.fetchall()

            # 2. Companies
            cursor.execute("""
                SELECT
                    company_id,
                    company_name,
                    industry,
                    description,
                    website,
                    location
                FROM companies
            """)

            companies = cursor.fetchall()

            # 3. Active skills
            cursor.execute("""
                SELECT
                    skill_id,
                    skill_name,
                    skill_category,
                    description
                FROM skills
                WHERE is_active = TRUE
            """)

            skills = cursor.fetchall()

            # 4. Student skills
            cursor.execute("""
                SELECT
                    student_id,
                    skill_id,
                    proficiency_level,
                    years_experience
                FROM student_skills
            """)

            student_skills = cursor.fetchall()

            # 5. Student projects
            cursor.execute("""
                SELECT
                    project_id,
                    student_id,
                    project_title,
                    project_description,
                    project_url,
                    start_date,
                    end_date
                FROM student_projects
            """)

            projects = cursor.fetchall()

            # 6. Project skills
            cursor.execute("""
                SELECT
                    project_id,
                    skill_id
                FROM project_skills
            """)

            project_skills = cursor.fetchall()

            # 7. Internships
            cursor.execute("""
                SELECT
                    internship_id,
                    company_id,
                    title,
                    description,
                    work_mode,
                    location,
                    stipend,
                    duration_months,
                    minimum_cgpa,
                    minimum_year,
                    application_deadline,
                    status
                FROM internships
            """)

            internships = cursor.fetchall()

            # 8. Internship skills
            cursor.execute("""
                SELECT
                    internship_id,
                    skill_id,
                    requirement_type,
                    minimum_proficiency,
                    importance_weight
                FROM internship_skills
            """)

            internship_skills = cursor.fetchall()

        return {
            "students": students,
            "companies": companies,
            "skills": skills,
            "student_skills": student_skills,
            "projects": projects,
            "project_skills": project_skills,
            "internships": internships,
            "internship_skills": internship_skills
        }

    finally:
        connection.close()


# ============================================================
# 2. DATA NORMALIZATION
# ============================================================

def normalize_data(data):
    """
    Convert PostgreSQL values into Neo4j-compatible values.
    """

    if isinstance(data, dict):
        return {
            key: normalize_data(value)
            for key, value in data.items()
        }

    if isinstance(data, (tuple, list)):
        return [
            normalize_data(value)
            for value in data
        ]

    if isinstance(data, Decimal):
        return float(data)

    if isinstance(data, (date, datetime)):
        return data.isoformat()

    return data


# ============================================================
# 3. STUDENT NODE SYNCHRONIZATION
# ============================================================

def sync_students(session, students):

    query = """
    UNWIND $students AS row

    MERGE (s:Student {
        student_id: row[0]
    })

    SET
        s.name = row[1],
        s.email = row[2],
        s.department = row[3],
        s.year_of_study = row[4],
        s.cgpa = row[5],
        s.graduation_year = row[6]
    """

    session.run(
        query,
        students=students
    ).consume()


# ============================================================
# 4. COMPANY NODE SYNCHRONIZATION
# ============================================================

def sync_companies(session, companies):

    query = """
    UNWIND $companies AS row

    MERGE (c:Company {
        company_id: row[0]
    })

    SET
        c.name = row[1],
        c.industry = row[2],
        c.description = row[3],
        c.website = row[4],
        c.location = row[5]
    """

    session.run(
        query,
        companies=companies
    ).consume()


# ============================================================
# 5. SKILL NODE SYNCHRONIZATION
# ============================================================

def sync_skills(session, skills):

    query = """
    UNWIND $skills AS row

    MERGE (s:Skill {
        skill_id: row[0]
    })

    SET
        s.name = row[1],
        s.category = row[2],
        s.description = row[3]
    """

    session.run(
        query,
        skills=skills
    ).consume()


# ============================================================
# 6. PROJECT NODE SYNCHRONIZATION
# ============================================================

def sync_projects(session, projects):

    query = """
    UNWIND $projects AS row

    MERGE (p:Project {
        project_id: row[0]
    })

    SET
        p.title = row[2],
        p.description = row[3],
        p.url = row[4],
        p.student_id = row[1],
        p.start_date = row[5],
        p.end_date = row[6]
    """

    session.run(
        query,
        projects=projects
    ).consume()


# ============================================================
# 7. INTERNSHIP NODE SYNCHRONIZATION
# ============================================================

def sync_internships(session, internships):

    query = """
    UNWIND $internships AS row

    MERGE (i:Internship {
        internship_id: row[0]
    })

    SET
        i.company_id = row[1],
        i.title = row[2],
        i.description = row[3],
        i.work_mode = row[4],
        i.location = row[5],
        i.stipend = row[6],
        i.duration_months = row[7],
        i.minimum_cgpa = row[8],
        i.minimum_year = row[9],
        i.application_deadline = row[10],
        i.status = row[11]
    """

    session.run(
        query,
        internships=internships
    ).consume()


# ============================================================
# 8. STUDENT-SKILL RELATIONSHIPS
# ============================================================

def sync_student_skills(session, relationships):

    query = """
    UNWIND $relationships AS row

    MATCH (s:Student {
        student_id: row[0]
    })

    MATCH (sk:Skill {
        skill_id: row[1]
    })

    MERGE (s)-[r:HAS_SKILL {
        managed_by: 'graph_sync_service'
    }]->(sk)

    SET
        r.proficiency_level = row[2],
        r.years_experience = row[3]
    """

    session.run(
        query,
        relationships=relationships
    ).consume()


# ============================================================
# 9. STUDENT-PROJECT RELATIONSHIPS
# ============================================================

def sync_student_projects(session, projects):

    query = """
    UNWIND $projects AS row

    MATCH (s:Student {
        student_id: row[1]
    })

    MATCH (p:Project {
        project_id: row[0]
    })

    MERGE (s)-[r:COMPLETED {
        managed_by: 'graph_sync_service'
    }]->(p)
    """

    session.run(
        query,
        projects=projects
    ).consume()


# ============================================================
# 10. PROJECT-SKILL RELATIONSHIPS
# ============================================================

def sync_project_skills(session, relationships):

    query = """
    UNWIND $relationships AS row

    MATCH (p:Project {
        project_id: row[0]
    })

    MATCH (sk:Skill {
        skill_id: row[1]
    })

    MERGE (p)-[r:USES_SKILL {
        managed_by: 'graph_sync_service'
    }]->(sk)
    """

    session.run(
        query,
        relationships=relationships
    ).consume()


# ============================================================
# 11. INTERNSHIP-SKILL RELATIONSHIPS
# ============================================================

def sync_internship_skills(session, relationships):

    query = """
    UNWIND $relationships AS row

    MATCH (i:Internship {
        internship_id: row[0]
    })

    MATCH (sk:Skill {
        skill_id: row[1]
    })

    MERGE (i)-[r:REQUIRES_SKILL {
        managed_by: 'graph_sync_service'
    }]->(sk)

    SET
        r.requirement_type = row[2],
        r.minimum_proficiency = row[3],
        r.importance_weight = row[4]
    """

    session.run(
        query,
        relationships=relationships
    ).consume()


# ============================================================
# 12. COMPANY-INTERNSHIP RELATIONSHIPS
# ============================================================

def sync_company_internships(session, internships):

    query = """
    UNWIND $internships AS row

    MATCH (c:Company {
        company_id: row[1]
    })

    MATCH (i:Internship {
        internship_id: row[0]
    })

    MERGE (c)-[r:OFFERS {
        managed_by: 'graph_sync_service'
    }]->(i)
    """

    session.run(
        query,
        internships=internships
    ).consume()


# ============================================================
# 13. REMOVE OUTDATED RELATIONSHIPS
# ============================================================

def remove_managed_relationships(session):

    relationship_types = [
        "HAS_SKILL",
        "COMPLETED",
        "USES_SKILL",
        "REQUIRES_SKILL",
        "OFFERS"
    ]

    for relationship_type in relationship_types:

        query = f"""
        MATCH ()-[r:{relationship_type}]->()
        WHERE r.managed_by = 'graph_sync_service'
        DELETE r
        """

        session.run(query).consume()


# ============================================================
# 14. REMOVE STALE NODES
# ============================================================

def remove_stale_nodes(session, data):
    """
    Remove nodes that no longer exist in PostgreSQL.

    This assumes these labels are exclusively managed
    by this synchronization service.
    """

    cleanup_queries = [
        (
            "Student",
            "student_id",
            [row[0] for row in data["students"]]
        ),
        (
            "Company",
            "company_id",
            [row[0] for row in data["companies"]]
        ),
        (
            "Skill",
            "skill_id",
            [row[0] for row in data["skills"]]
        ),
        (
            "Project",
            "project_id",
            [row[0] for row in data["projects"]]
        ),
        (
            "Internship",
            "internship_id",
            [row[0] for row in data["internships"]]
        )
    ]

    for label, identifier, ids in cleanup_queries:

        query = f"""
        MATCH (n:{label})

        WHERE NOT (
            n.{identifier} IN $ids
        )

        DETACH DELETE n
        """

        session.run(
            query,
            ids=ids
        ).consume()


# ============================================================
# 15. GRAPH SYNCHRONIZATION METADATA
# ============================================================

def update_sync_metadata(session):

    query = """
    MERGE (m:GraphMetadata {
        name: 'postgresql_sync'
    })

    SET
        m.last_synced_at = datetime(),
        m.status = 'success'
    """

    session.run(query).consume()


# ============================================================
# 16. MAIN GRAPH SYNCHRONIZATION
# ============================================================

def synchronize_graph():
    """
    Synchronize PostgreSQL data with Neo4j.

    PostgreSQL acts as the source of truth.
    All Neo4j synchronization operations execute
    inside a single write transaction.
    """

    # 1. Fetch PostgreSQL records
    raw_data = fetch_graph_data()

    # 2. Normalize PostgreSQL values
    data = normalize_data(raw_data)

    def sync_transaction(tx):

        # 3. Remove previously managed relationships
        remove_managed_relationships(tx)

        # 4. Synchronize nodes
        sync_students(
            tx,
            data["students"]
        )

        sync_companies(
            tx,
            data["companies"]
        )

        sync_skills(
            tx,
            data["skills"]
        )

        sync_projects(
            tx,
            data["projects"]
        )

        sync_internships(
            tx,
            data["internships"]
        )

        # 5. Synchronize relationships
        sync_student_skills(
            tx,
            data["student_skills"]
        )

        sync_student_projects(
            tx,
            data["projects"]
        )

        sync_project_skills(
            tx,
            data["project_skills"]
        )

        sync_internship_skills(
            tx,
            data["internship_skills"]
        )

        sync_company_internships(
            tx,
            data["internships"]
        )

        # 6. Remove outdated nodes
        remove_stale_nodes(
            tx,
            data
        )

        # 7. Update synchronization metadata
        update_sync_metadata(tx)

        # 8. Return synchronization counts
        return {
            "students": len(data["students"]),
            "companies": len(data["companies"]),
            "skills": len(data["skills"]),
            "projects": len(data["projects"]),
            "internships": len(data["internships"]),
            "student_skills": len(data["student_skills"]),
            "project_skills": len(data["project_skills"]),
            "internship_skills": len(data["internship_skills"])
        }

    # 9. Execute Neo4j transaction
    with driver.session() as session:

        counts = session.execute_write(
            sync_transaction
        )

    # 10. Return result
    return {
        "status": "success",
        "message": (
            "PostgreSQL data successfully synchronized "
            "with Neo4j."
        ),
        "counts": counts
    }
    # ============================================================
# 17. SYNCHRONIZE INDIVIDUAL STUDENT SKILL
# ============================================================

def synchronize_student_skill(student_id: int, skill_id: int):
    """
    Synchronize one student's skill proficiency from
    PostgreSQL to Neo4j.

    PostgreSQL remains the source of truth.
    """

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    ss.student_id,
                    ss.skill_id,
                    ss.proficiency_level,
                    ss.years_experience,
                    sk.skill_name,
                    sk.skill_category
                FROM student_skills AS ss
                JOIN skills AS sk
                    ON ss.skill_id = sk.skill_id
                WHERE ss.student_id = %s
                  AND ss.skill_id = %s
                """,
                (student_id, skill_id)
            )

            row = cursor.fetchone()

    finally:

        connection.close()

    # Check whether the student has this skill.
    if row is None:

        with driver.session() as session:

            session.run(
                """
                MATCH (s:Student {student_id: $student_id})
                MATCH (sk:Skill {skill_id: $skill_id})

                MATCH (s)-[r:HAS_SKILL {
                    managed_by: 'graph_sync_service'
                }]->(sk)

                DELETE r
                """,
                student_id=student_id,
                skill_id=skill_id
            ).consume()

        return {
            "status": "success",
            "message": "Student skill relationship removed from Neo4j."
        }

    # Extract PostgreSQL values.
    student_id = row[0]
    skill_id = row[1]
    proficiency_level = row[2]
    years_experience = float(row[3])
    skill_name = row[4]
    skill_category = row[5]

    # Synchronize the relationship in Neo4j.
    with driver.session() as session:

        result = session.run(
            """
            MATCH (s:Student {student_id: $student_id})
            MATCH (sk:Skill {skill_id: $skill_id})

            MERGE (s)-[r:HAS_SKILL {
                managed_by: 'graph_sync_service'
            }]->(sk)

            SET
                r.proficiency_level = $proficiency_level,
                r.years_experience = $years_experience

            RETURN
                s.student_id AS student_id,
                sk.skill_id AS skill_id,
                r.proficiency_level AS proficiency_level
            """,
            student_id=student_id,
            skill_id=skill_id,
            proficiency_level=proficiency_level,
            years_experience=years_experience
        )

        synchronized_record = result.single()

        if synchronized_record is None:

            raise RuntimeError(
                "Student or skill node not found in Neo4j. "
                "Run the full graph synchronization first."
            )

    return {
        "status": "success",
        "student_id": student_id,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "skill_category": skill_category,
        "proficiency_level": proficiency_level,
        "message": "Student skill successfully synchronized with Neo4j."
    }