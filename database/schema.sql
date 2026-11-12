-- ============================================================
-- SKILLBRIDGE
-- Explainable Internship Matching and Skill-Gap Analysis
-- PostgreSQL 16 + pgvector
CREATE EXTENSION IF NOT EXISTS vector;
-- ============================================================
BEGIN;
-- ============================================================
-- 1. ROLES
-- ============================================================
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE,
    description VARCHAR(255)
);
-- ============================================================
-- 2. USERS
-- ============================================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(role_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_users_email CHECK (POSITION('@' IN email) > 1)
);
-- ============================================================
-- 3. STUDENTS
-- ============================================================
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    registration_number VARCHAR(30) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    year_of_study INTEGER NOT NULL,
    cgpa NUMERIC(4, 2) NOT NULL,
    graduation_year INTEGER NOT NULL,
    bio TEXT,
    CONSTRAINT fk_students_user FOREIGN KEY (student_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_students_year CHECK (
        year_of_study BETWEEN 1 AND 6
    ),
    CONSTRAINT chk_students_cgpa CHECK (
        cgpa BETWEEN 0 AND 10
    ),
    CONSTRAINT chk_students_graduation_year CHECK (graduation_year >= 2024)
);
-- ============================================================
-- 4. COMPANIES
-- ============================================================
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    industry VARCHAR(100) NOT NULL,
    description TEXT,
    website VARCHAR(255),
    location VARCHAR(100),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_companies_verification CHECK (
        verification_status IN ('Pending', 'Verified', 'Rejected')
    )
);
-- ============================================================
-- 5. RECRUITERS
-- ============================================================
CREATE TABLE recruiters (
    recruiter_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    designation VARCHAR(100) NOT NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    CONSTRAINT fk_recruiters_user FOREIGN KEY (recruiter_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_recruiters_company FOREIGN KEY (company_id) REFERENCES companies(company_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_recruiters_verification CHECK (
        verification_status IN ('Pending', 'Verified', 'Rejected')
    )
);
-- ============================================================
-- 6. SKILLS
-- ============================================================
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(80) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
-- ============================================================
-- 7. STUDENT_SKILLS
-- ============================================================
CREATE TABLE student_skills (
    student_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    proficiency_level INTEGER NOT NULL,
    years_experience NUMERIC(4, 1) NOT NULL DEFAULT 0,
    last_used_date DATE,
    PRIMARY KEY (student_id, skill_id),
    CONSTRAINT fk_student_skills_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_student_skills_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_student_skill_proficiency CHECK (
        proficiency_level BETWEEN 1 AND 5
    ),
    CONSTRAINT chk_student_skill_experience CHECK (years_experience >= 0)
);
-- ============================================================
-- 8. STUDENT_PROJECTS
-- ============================================================
CREATE TABLE student_projects (
    project_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    project_title VARCHAR(150) NOT NULL,
    project_description TEXT NOT NULL,
    project_url VARCHAR(255),
    start_date DATE,
    end_date DATE,
    CONSTRAINT fk_student_projects_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_student_project_dates CHECK (
        end_date IS NULL
        OR start_date IS NULL
        OR end_date >= start_date
    )
);
-- ============================================================
-- 9. PROJECT_SKILLS
-- ============================================================
CREATE TABLE project_skills (
    project_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (project_id, skill_id),
    CONSTRAINT fk_project_skills_project FOREIGN KEY (project_id) REFERENCES student_projects(project_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_project_skills_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON UPDATE CASCADE ON DELETE RESTRICT
);
-- ============================================================
-- 10. INTERNSHIPS
-- ============================================================
CREATE TABLE internships (
    internship_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    work_mode VARCHAR(20) NOT NULL,
    location VARCHAR(100),
    stipend NUMERIC(10, 2) NOT NULL DEFAULT 0,
    duration_months INTEGER NOT NULL,
    available_positions INTEGER NOT NULL,
    minimum_cgpa NUMERIC(4, 2) NOT NULL DEFAULT 0,
    minimum_year INTEGER NOT NULL,
    application_deadline DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_internships_company FOREIGN KEY (company_id) REFERENCES companies(company_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_internships_recruiter FOREIGN KEY (created_by) REFERENCES recruiters(recruiter_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_internships_work_mode CHECK (work_mode IN ('Remote', 'Hybrid', 'On-site')),
    CONSTRAINT chk_internships_stipend CHECK (stipend >= 0),
    CONSTRAINT chk_internships_duration CHECK (
        duration_months BETWEEN 1 AND 24
    ),
    CONSTRAINT chk_internships_positions CHECK (available_positions > 0),
    CONSTRAINT chk_internships_cgpa CHECK (
        minimum_cgpa BETWEEN 0 AND 10
    ),
    CONSTRAINT chk_internships_year CHECK (
        minimum_year BETWEEN 1 AND 6
    ),
    CONSTRAINT chk_internships_status CHECK (status IN ('Draft', 'Open', 'Closed', 'Expired'))
);
-- ============================================================
-- 11. INTERNSHIP_SKILLS
-- ============================================================
CREATE TABLE internship_skills (
    internship_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    requirement_type VARCHAR(20) NOT NULL,
    minimum_proficiency INTEGER NOT NULL,
    importance_weight NUMERIC(5, 2) NOT NULL DEFAULT 1.00,
    PRIMARY KEY (internship_id, skill_id),
    CONSTRAINT fk_internship_skills_internship FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_internship_skills_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_internship_requirement_type CHECK (requirement_type IN ('Required', 'Preferred')),
    CONSTRAINT chk_internship_minimum_proficiency CHECK (
        minimum_proficiency BETWEEN 1 AND 5
    ),
    CONSTRAINT chk_internship_importance CHECK (importance_weight > 0)
);
-- ============================================================
-- 12. APPLICATIONS
-- ============================================================
CREATE TABLE applications (
    application_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    internship_id INTEGER NOT NULL,
    resume_reference VARCHAR(255),
    cover_letter TEXT,
    match_score NUMERIC(5, 2),
    status VARCHAR(20) NOT NULL DEFAULT 'Applied',
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_applications_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_applications_internship FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_student_internship_application UNIQUE (student_id, internship_id),
    CONSTRAINT chk_applications_match_score CHECK (
        match_score IS NULL
        OR match_score BETWEEN 0 AND 100
    ),
    CONSTRAINT chk_applications_status CHECK (
        status IN (
            'Applied',
            'Under Review',
            'Shortlisted',
            'Interview',
            'Selected',
            'Rejected',
            'Withdrawn'
        )
    )
);
-- ============================================================
-- 13. APPLICATION_STATUS_HISTORY
-- ============================================================
CREATE TABLE application_status_history (
    history_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    changed_by INTEGER NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    remarks TEXT,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_status_history_application FOREIGN KEY (application_id) REFERENCES applications(application_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_status_history_user FOREIGN KEY (changed_by) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_status_history_new_status CHECK (
        new_status IN (
            'Applied',
            'Under Review',
            'Shortlisted',
            'Interview',
            'Selected',
            'Rejected',
            'Withdrawn'
        )
    )
);
-- ============================================================
-- 14. INTERVIEWS
-- ============================================================
CREATE TABLE interviews (
    interview_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    scheduled_by INTEGER NOT NULL,
    interview_round VARCHAR(50) NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    mode VARCHAR(20) NOT NULL,
    meeting_link VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
    remarks TEXT,
    CONSTRAINT fk_interviews_application FOREIGN KEY (application_id) REFERENCES applications(application_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_interviews_recruiter FOREIGN KEY (scheduled_by) REFERENCES recruiters(recruiter_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_interview_mode CHECK (mode IN ('Online', 'Offline')),
    CONSTRAINT chk_interview_status CHECK (
        status IN (
            'Scheduled',
            'Completed',
            'Cancelled',
            'Rescheduled'
        )
    )
);
-- ============================================================
-- 15. INTERVIEW_EVALUATIONS
-- ============================================================
CREATE TABLE interview_evaluations (
    evaluation_id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL UNIQUE,
    technical_score INTEGER,
    communication_score INTEGER,
    problem_solving_score INTEGER,
    overall_score NUMERIC(5, 2),
    comments TEXT,
    recommendation VARCHAR(20),
    CONSTRAINT fk_evaluations_interview FOREIGN KEY (interview_id) REFERENCES interviews(interview_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_technical_score CHECK (
        technical_score IS NULL
        OR technical_score BETWEEN 0 AND 10
    ),
    CONSTRAINT chk_communication_score CHECK (
        communication_score IS NULL
        OR communication_score BETWEEN 0 AND 10
    ),
    CONSTRAINT chk_problem_solving_score CHECK (
        problem_solving_score IS NULL
        OR problem_solving_score BETWEEN 0 AND 10
    ),
    CONSTRAINT chk_overall_score CHECK (
        overall_score IS NULL
        OR overall_score BETWEEN 0 AND 100
    ),
    CONSTRAINT chk_recommendation CHECK (
        recommendation IS NULL
        OR recommendation IN ('Select', 'Reject', 'Review')
    )
);
-- ============================================================
-- 16. STUDENT_PREFERENCES
-- ============================================================
CREATE TABLE student_preferences (
    preference_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL UNIQUE,
    preferred_domain VARCHAR(100),
    preferred_location VARCHAR(100),
    preferred_work_mode VARCHAR(20),
    minimum_stipend NUMERIC(10, 2) NOT NULL DEFAULT 0,
    preferred_duration INTEGER,
    CONSTRAINT fk_student_preferences_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_preference_work_mode CHECK (
        preferred_work_mode IS NULL
        OR preferred_work_mode IN ('Remote', 'Hybrid', 'On-site')
    ),
    CONSTRAINT chk_preference_stipend CHECK (minimum_stipend >= 0),
    CONSTRAINT chk_preference_duration CHECK (
        preferred_duration IS NULL
        OR preferred_duration BETWEEN 1 AND 24
    )
);
-- ============================================================
-- 17. SAVED_INTERNSHIPS
-- ============================================================
CREATE TABLE saved_internships (
    saved_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    internship_id INTEGER NOT NULL,
    saved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_saved_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_saved_internship FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_saved_internship UNIQUE (student_id, internship_id)
);
-- ============================================================
-- 18. FEEDBACK
-- ============================================================
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL,
    submitted_by INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comments TEXT,
    feedback_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_application FOREIGN KEY (application_id) REFERENCES applications(application_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_feedback_user FOREIGN KEY (submitted_by) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_feedback_rating CHECK (
        rating BETWEEN 1 AND 5
    ),
    CONSTRAINT chk_feedback_type CHECK (feedback_type IN ('Student', 'Recruiter'))
);
-- ============================================================
-- 19. STUDENT_EMBEDDINGS
-- ============================================================
CREATE TABLE student_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL UNIQUE,
    source_text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_embeddings_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE ON DELETE CASCADE
);
-- ============================================================
-- 20. INTERNSHIP_EMBEDDINGS
-- ============================================================
CREATE TABLE internship_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    internship_id INTEGER NOT NULL UNIQUE,
    source_text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_internship_embeddings_internship FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON UPDATE CASCADE ON DELETE CASCADE
);
COMMIT;
-- ============================================================
-- END OF SKILLBRIDGE SCHEMA
-- ============================================================