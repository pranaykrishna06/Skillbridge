-- ============================================================
-- SKILLBRIDGE
-- ADVANCED DATABASE FEATURES
-- PostgreSQL 16 + pgvector
-- ============================================================
-- ============================================================
-- 1. INDEXES
-- Improve query performance
-- ============================================================
-- User and student indexes
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_students_department ON students(department);
CREATE INDEX IF NOT EXISTS idx_students_cgpa ON students(cgpa);
-- Company and recruiter indexes
CREATE INDEX IF NOT EXISTS idx_recruiters_company_id ON recruiters(company_id);
-- Internship indexes
CREATE INDEX IF NOT EXISTS idx_internships_company_id ON internships(company_id);
CREATE INDEX IF NOT EXISTS idx_internships_status ON internships(status);
CREATE INDEX IF NOT EXISTS idx_internships_deadline ON internships(application_deadline);
-- Skill matching indexes
CREATE INDEX IF NOT EXISTS idx_student_skills_skill_id ON student_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_internship_skills_skill_id ON internship_skills(skill_id);
-- Application indexes
CREATE INDEX IF NOT EXISTS idx_applications_student_id ON applications(student_id);
CREATE INDEX IF NOT EXISTS idx_applications_internship_id ON applications(internship_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
-- Interview indexes
CREATE INDEX IF NOT EXISTS idx_interviews_scheduled_at ON interviews(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_interviews_application_id ON interviews(application_id);
-- ============================================================
-- 2. VIEWS
-- Provide simplified access to frequently used information
-- ============================================================
-- View 1: Student application summary
CREATE OR REPLACE VIEW v_student_application_summary AS
SELECT s.student_id,
    u.full_name AS student_name,
    s.department,
    s.cgpa,
    COUNT(a.application_id) AS total_applications,
    COUNT(a.application_id) FILTER (
        WHERE a.status = 'Selected'
    ) AS selected_applications,
    COUNT(a.application_id) FILTER (
        WHERE a.status = 'Rejected'
    ) AS rejected_applications,
    COUNT(a.application_id) FILTER (
        WHERE a.status = 'Shortlisted'
    ) AS shortlisted_applications
FROM students s
    JOIN users u ON s.student_id = u.user_id
    LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY s.student_id,
    u.full_name,
    s.department,
    s.cgpa;
-- View 2: Internship application summary
CREATE OR REPLACE VIEW v_internship_application_summary AS
SELECT i.internship_id,
    i.title AS internship_title,
    c.company_name,
    i.status AS internship_status,
    i.stipend,
    COUNT(a.application_id) AS total_applications,
    COUNT(a.application_id) FILTER (
        WHERE a.status = 'Selected'
    ) AS selected_candidates,
    COUNT(a.application_id) FILTER (
        WHERE a.status = 'Shortlisted'
    ) AS shortlisted_candidates
FROM internships i
    JOIN companies c ON i.company_id = c.company_id
    LEFT JOIN applications a ON i.internship_id = a.internship_id
GROUP BY i.internship_id,
    i.title,
    c.company_name,
    i.status,
    i.stipend;
-- View 3: Internship skill requirements
CREATE OR REPLACE VIEW v_internship_skill_requirements AS
SELECT i.internship_id,
    i.title AS internship_title,
    sk.skill_id,
    sk.skill_name,
    isk.requirement_type,
    isk.minimum_proficiency,
    isk.importance_weight
FROM internships i
    JOIN internship_skills isk ON i.internship_id = isk.internship_id
    JOIN skills sk ON isk.skill_id = sk.skill_id;
-- ============================================================
-- 3. STORED FUNCTIONS
-- ============================================================
-- Function 1:
-- Check whether a student is eligible for an internship.
CREATE OR REPLACE FUNCTION is_student_eligible(
        p_student_id INTEGER,
        p_internship_id INTEGER
    ) RETURNS BOOLEAN LANGUAGE plpgsql AS $$
DECLARE v_eligible BOOLEAN;
BEGIN
SELECT (
        s.cgpa >= i.minimum_cgpa
        AND s.year_of_study >= i.minimum_year
        AND i.application_deadline >= CURRENT_DATE
        AND i.status = 'Open'
        AND i.available_positions > 0
    ) INTO v_eligible
FROM students s
    CROSS JOIN internships i
WHERE s.student_id = p_student_id
    AND i.internship_id = p_internship_id;
RETURN COALESCE(v_eligible, FALSE);
END;
$$;
-- Function 2:
-- Calculate a student's skill match percentage
-- for a particular internship.
CREATE OR REPLACE FUNCTION calculate_skill_match(
        p_student_id INTEGER,
        p_internship_id INTEGER
    ) RETURNS NUMERIC(5, 2) LANGUAGE plpgsql AS $$
DECLARE v_match_score NUMERIC(5, 2);
BEGIN
SELECT CASE
        WHEN COALESCE(SUM(isk.importance_weight), 0) = 0 THEN 0
        ELSE ROUND(
            100.0 * SUM(
                isk.importance_weight * CASE
                    WHEN ss.proficiency_level IS NULL THEN 0
                    WHEN ss.proficiency_level >= isk.minimum_proficiency THEN 1
                    ELSE ss.proficiency_level::NUMERIC / isk.minimum_proficiency
                END
            ) / SUM(isk.importance_weight),
            2
        )
    END INTO v_match_score
FROM internship_skills isk
    LEFT JOIN student_skills ss ON isk.skill_id = ss.skill_id
    AND ss.student_id = p_student_id
WHERE isk.internship_id = p_internship_id;
RETURN COALESCE(v_match_score, 0);
END;
$$;
-- Function 3:
-- Identify the skills a student needs to improve.
CREATE OR REPLACE FUNCTION get_student_skill_gaps(
        p_student_id INTEGER,
        p_internship_id INTEGER
    ) RETURNS TABLE (
        skill_name VARCHAR,
        required_proficiency INTEGER,
        student_proficiency INTEGER,
        requirement_type VARCHAR,
        proficiency_gap INTEGER
    ) LANGUAGE sql AS $$
SELECT sk.skill_name,
    isk.minimum_proficiency,
    COALESCE(ss.proficiency_level, 0),
    isk.requirement_type,
    GREATEST(
        isk.minimum_proficiency - COALESCE(ss.proficiency_level, 0),
        0
    )
FROM internship_skills isk
    JOIN skills sk ON isk.skill_id = sk.skill_id
    LEFT JOIN student_skills ss ON isk.skill_id = ss.skill_id
    AND ss.student_id = p_student_id
WHERE isk.internship_id = p_internship_id
    AND COALESCE(ss.proficiency_level, 0) < isk.minimum_proficiency;
$$;
-- ============================================================
-- 4. TRIGGERS
-- Automatically maintain database information
-- ============================================================
-- Trigger 1:
-- Automatically update the updated_at column
-- whenever an application is modified.
CREATE OR REPLACE FUNCTION update_application_timestamp() RETURNS TRIGGER LANGUAGE plpgsql AS $$ BEGIN NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS trg_update_application_timestamp ON applications;
CREATE TRIGGER trg_update_application_timestamp BEFORE
UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_application_timestamp();
-- Trigger 2:
-- Automatically record application status changes.
--
-- The application must set the current user's ID using:
-- SET LOCAL app.user_id = '8';
--
-- This allows the trigger to record who made the change.
CREATE OR REPLACE FUNCTION log_application_status_change() RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE v_changed_by INTEGER;
BEGIN IF OLD.status IS DISTINCT
FROM NEW.status THEN v_changed_by := NULLIF(current_setting('app.user_id', TRUE), '')::INTEGER;
IF v_changed_by IS NULL THEN RAISE EXCEPTION 'Set app.user_id before changing application status';
END IF;
INSERT INTO application_status_history (
        application_id,
        changed_by,
        old_status,
        new_status,
        remarks,
        changed_at
    )
VALUES (
        NEW.application_id,
        v_changed_by,
        OLD.status,
        NEW.status,
        'Status automatically recorded by database trigger',
        CURRENT_TIMESTAMP
    );
END IF;
RETURN NEW;
END;
$$;
DROP TRIGGER IF EXISTS trg_application_status_history ON applications;
CREATE TRIGGER trg_application_status_history
AFTER
UPDATE OF status ON applications FOR EACH ROW EXECUTE FUNCTION log_application_status_change();
-- ============================================================
-- 5. VECTOR SEARCH INDEX
-- Supports semantic similarity search using pgvector
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_student_embeddings_hnsw ON student_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_internship_embeddings_hnsw ON internship_embeddings USING hnsw (embedding vector_cosine_ops);
-- ============================================================
-- END OF ADVANCED DATABASE FEATURES
-- ============================================================