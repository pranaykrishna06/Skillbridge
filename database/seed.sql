-- ============================================================
-- SKILLBRIDGE SAMPLE DATA
-- PostgreSQL 16
-- ============================================================
BEGIN;
-- ============================================================
-- 1. ROLES
-- ============================================================
INSERT INTO roles (role_id, role_name, description)
VALUES (1, 'Admin', 'System administrator'),
    (2, 'Student', 'Student seeking internships'),
    (3, 'Recruiter', 'Company recruiter');
-- ============================================================
-- 2. USERS
-- Demo password for all users: SkillBridge@123
-- Passwords are hashed using bcrypt through pgcrypto.
-- ============================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO users (
        user_id,
        role_id,
        full_name,
        email,
        password_hash,
        phone,
        is_verified,
        is_active
    )
VALUES (
        1,
        1,
        'System Admin',
        'admin@skillbridge.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000001',
        TRUE,
        TRUE
    ),
    (
        2,
        2,
        'Aarav Sharma',
        'aarav@gmail.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000002',
        TRUE,
        TRUE
    ),
    (
        3,
        2,
        'Ananya Rao',
        'ananya@gmail.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000003',
        TRUE,
        TRUE
    ),
    (
        4,
        2,
        'Rahul Verma',
        'rahul@gmail.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000004',
        TRUE,
        TRUE
    ),
    (
        5,
        2,
        'Priya Nair',
        'priya@gmail.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000005',
        TRUE,
        TRUE
    ),
    (
        6,
        2,
        'Arjun Reddy',
        'arjun@gmail.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000006',
        TRUE,
        TRUE
    ),
    (
        7,
        2,
        'Sneha Kulkarni',
        'sneha@gmail.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000007',
        TRUE,
        TRUE
    ),
    (
        8,
        3,
        'Karan Mehta',
        'karan@techsolutions.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000008',
        TRUE,
        TRUE
    ),
    (
        9,
        3,
        'Divya Menon',
        'divya@dataworks.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000009',
        TRUE,
        TRUE
    ),
    (
        10,
        3,
        'Rohit Kapoor',
        'rohit@cloudtech.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000010',
        TRUE,
        TRUE
    ),
    (
        11,
        3,
        'Meera Iyer',
        'meera@innovate.com',
        crypt('SkillBridge@123', gen_salt('bf', 12)),
        '9000000011',
        TRUE,
        TRUE
    );
-- ============================================================
-- 3. STUDENTS
-- ============================================================
INSERT INTO students (
        student_id,
        registration_number,
        department,
        year_of_study,
        cgpa,
        graduation_year,
        bio
    )
VALUES (
        2,
        'PES1UG24CS101',
        'Computer Science',
        3,
        8.90,
        2027,
        'Interested in full stack development and software engineering.'
    ),
    (
        3,
        'PES1UG24CS102',
        'Computer Science',
        3,
        9.20,
        2027,
        'Interested in machine learning, artificial intelligence and Python.'
    ),
    (
        4,
        'PES1UG24CS103',
        'Information Science',
        3,
        8.10,
        2027,
        'Aspiring backend developer with database experience.'
    ),
    (
        5,
        'PES1UG24CS104',
        'Computer Science',
        2,
        8.75,
        2028,
        'Interested in data analytics and visualization.'
    ),
    (
        6,
        'PES1UG24CS105',
        'Computer Science',
        3,
        7.80,
        2027,
        'Interested in cloud computing and DevOps.'
    ),
    (
        7,
        'PES1UG24CS106',
        'Electronics and Communication',
        2,
        9.00,
        2028,
        'Interested in software development and cybersecurity.'
    );
-- ============================================================
-- 4. COMPANIES
-- ============================================================
INSERT INTO companies (
        company_id,
        company_name,
        registration_number,
        industry,
        description,
        website,
        location,
        verification_status
    )
VALUES (
        1,
        'TechSolutions',
        'REG001',
        'Software Development',
        'Software engineering and application development company.',
        'https://example.com/techsolutions',
        'Bengaluru',
        'Verified'
    ),
    (
        2,
        'DataWorks',
        'REG002',
        'Data Analytics',
        'Data science and business intelligence company.',
        'https://example.com/dataworks',
        'Hyderabad',
        'Verified'
    ),
    (
        3,
        'CloudTech',
        'REG003',
        'Cloud Computing',
        'Cloud infrastructure and DevOps solutions company.',
        'https://example.com/cloudtech',
        'Bengaluru',
        'Verified'
    ),
    (
        4,
        'Innovate Labs',
        'REG004',
        'Artificial Intelligence',
        'AI research and technology development company.',
        'https://example.com/innovate',
        'Pune',
        'Verified'
    );
-- ============================================================
-- 5. RECRUITERS
-- ============================================================
INSERT INTO recruiters (
        recruiter_id,
        company_id,
        designation,
        verification_status
    )
VALUES (8, 1, 'Technical Recruiter', 'Verified'),
    (9, 2, 'HR Manager', 'Verified'),
    (10, 3, 'Talent Acquisition Manager', 'Verified'),
    (11, 4, 'Recruitment Lead', 'Verified');
-- ============================================================
-- 6. SKILLS
-- ============================================================
INSERT INTO skills (
        skill_id,
        skill_name,
        skill_category,
        description
    )
VALUES (
        1,
        'Python',
        'Programming',
        'Python programming language'
    ),
    (
        2,
        'Java',
        'Programming',
        'Java programming language'
    ),
    (
        3,
        'C++',
        'Programming',
        'C++ programming language'
    ),
    (
        4,
        'JavaScript',
        'Programming',
        'JavaScript development'
    ),
    (
        5,
        'React',
        'Frontend',
        'React frontend development'
    ),
    (
        6,
        'Node.js',
        'Backend',
        'Node.js backend development'
    ),
    (
        7,
        'SQL',
        'Database',
        'Relational database querying'
    ),
    (
        8,
        'PostgreSQL',
        'Database',
        'PostgreSQL database management'
    ),
    (
        9,
        'Machine Learning',
        'AI/ML',
        'Machine learning algorithms'
    ),
    (
        10,
        'Deep Learning',
        'AI/ML',
        'Deep learning techniques'
    ),
    (
        11,
        'Docker',
        'DevOps',
        'Containerization using Docker'
    ),
    (12, 'AWS', 'Cloud', 'Amazon Web Services'),
    (13, 'Git', 'Tools', 'Version control using Git'),
    (
        14,
        'HTML/CSS',
        'Frontend',
        'Web structure and styling'
    ),
    (
        15,
        'Data Analysis',
        'Analytics',
        'Data analysis and visualization'
    );
-- ============================================================
-- 7. STUDENT SKILLS
-- ============================================================
INSERT INTO student_skills (
        student_id,
        skill_id,
        proficiency_level,
        years_experience
    )
VALUES (2, 1, 4, 2.0),
    (2, 4, 4, 2.0),
    (2, 5, 3, 1.0),
    (2, 6, 3, 1.0),
    (2, 7, 4, 2.0),
    (2, 13, 4, 2.0),
    (3, 1, 5, 3.0),
    (3, 7, 4, 2.0),
    (3, 9, 5, 2.0),
    (3, 10, 4, 1.0),
    (3, 15, 4, 2.0),
    (4, 2, 4, 2.0),
    (4, 3, 3, 1.0),
    (4, 7, 5, 3.0),
    (4, 8, 4, 2.0),
    (4, 13, 3, 1.0),
    (5, 1, 4, 2.0),
    (5, 7, 4, 2.0),
    (5, 9, 3, 1.0),
    (5, 15, 5, 2.0),
    (6, 1, 3, 1.0),
    (6, 11, 4, 2.0),
    (6, 12, 4, 1.0),
    (6, 13, 4, 2.0),
    (7, 2, 4, 1.0),
    (7, 3, 4, 1.0),
    (7, 7, 3, 1.0),
    (7, 13, 3, 1.0);
-- ============================================================
-- 8. STUDENT PROJECTS
-- ============================================================
INSERT INTO student_projects (
        project_id,
        student_id,
        project_title,
        project_description,
        project_url,
        start_date,
        end_date
    )
VALUES (
        1,
        2,
        'E-Commerce Application',
        'Full stack shopping application using React and Node.js.',
        'https://example.com/project1',
        '2025-01-01',
        '2025-04-01'
    ),
    (
        2,
        3,
        'Student Performance Prediction',
        'Machine learning model to predict student performance.',
        'https://example.com/project2',
        '2025-02-01',
        '2025-05-01'
    ),
    (
        3,
        4,
        'Library Management System',
        'Database-driven library management application.',
        'https://example.com/project3',
        '2025-01-01',
        '2025-03-01'
    ),
    (
        4,
        5,
        'Sales Data Analysis',
        'Analysis of sales data using Python and visualization.',
        'https://example.com/project4',
        '2025-03-01',
        '2025-06-01'
    ),
    (
        5,
        6,
        'Cloud Deployment Project',
        'Deployment of a web application using AWS and Docker.',
        'https://example.com/project5',
        '2025-02-01',
        '2025-05-01'
    ),
    (
        6,
        7,
        'Secure Login System',
        'Authentication system with secure password handling.',
        'https://example.com/project6',
        '2025-04-01',
        '2025-06-01'
    );
-- ============================================================
-- 9. PROJECT SKILLS
-- ============================================================
INSERT INTO project_skills (project_id, skill_id)
VALUES (1, 4),
    (1, 5),
    (1, 6),
    (1, 7),
    (2, 1),
    (2, 9),
    (2, 15),
    (3, 2),
    (3, 7),
    (3, 8),
    (4, 1),
    (4, 7),
    (4, 15),
    (5, 11),
    (5, 12),
    (6, 2),
    (6, 7);
-- ============================================================
-- 10. INTERNSHIPS
-- ============================================================
INSERT INTO internships (
        internship_id,
        company_id,
        created_by,
        title,
        description,
        work_mode,
        location,
        stipend,
        duration_months,
        available_positions,
        minimum_cgpa,
        minimum_year,
        application_deadline,
        status
    )
VALUES (
        1,
        1,
        8,
        'Full Stack Developer Intern',
        'Develop web applications using React, Node.js and SQL.',
        'Hybrid',
        'Bengaluru',
        15000,
        3,
        3,
        7.50,
        2,
        '2026-12-15',
        'Open'
    ),
    (
        2,
        2,
        9,
        'Machine Learning Intern',
        'Build and evaluate machine learning models using Python.',
        'Remote',
        'Hyderabad',
        20000,
        6,
        2,
        8.00,
        3,
        '2026-12-20',
        'Open'
    ),
    (
        3,
        3,
        10,
        'Cloud Engineering Intern',
        'Work with AWS, Docker and cloud infrastructure.',
        'On-site',
        'Bengaluru',
        18000,
        4,
        2,
        7.00,
        2,
        '2026-12-25',
        'Open'
    ),
    (
        4,
        4,
        11,
        'AI Research Intern',
        'Assist in deep learning and artificial intelligence research.',
        'Remote',
        'Pune',
        25000,
        6,
        2,
        8.50,
        3,
        '2027-01-10',
        'Open'
    ),
    (
        5,
        1,
        8,
        'Backend Developer Intern',
        'Develop APIs and database-backed services.',
        'Hybrid',
        'Bengaluru',
        12000,
        3,
        2,
        7.00,
        2,
        '2026-12-18',
        'Open'
    ),
    (
        6,
        2,
        9,
        'Data Analyst Intern',
        'Analyze datasets and prepare business reports.',
        'Remote',
        'Hyderabad',
        14000,
        3,
        3,
        7.50,
        2,
        '2026-12-22',
        'Open'
    ),
    (
        7,
        3,
        10,
        'DevOps Intern',
        'Work with Docker, AWS and deployment pipelines.',
        'On-site',
        'Bengaluru',
        16000,
        4,
        2,
        7.00,
        2,
        '2027-01-05',
        'Open'
    ),
    (
        8,
        4,
        11,
        'Python Developer Intern',
        'Develop Python-based applications and automation tools.',
        'Hybrid',
        'Pune',
        17000,
        3,
        2,
        7.50,
        2,
        '2027-01-12',
        'Open'
    );
-- ============================================================
-- 11. INTERNSHIP SKILLS
-- ============================================================
INSERT INTO internship_skills (
        internship_id,
        skill_id,
        requirement_type,
        minimum_proficiency,
        importance_weight
    )
VALUES (1, 4, 'Required', 3, 1.50),
    (1, 5, 'Required', 3, 1.50),
    (1, 6, 'Required', 3, 1.30),
    (1, 7, 'Preferred', 2, 1.00),
    (2, 1, 'Required', 4, 1.50),
    (2, 9, 'Required', 4, 1.50),
    (2, 15, 'Preferred', 3, 1.00),
    (3, 11, 'Required', 3, 1.50),
    (3, 12, 'Required', 3, 1.50),
    (3, 13, 'Preferred', 2, 1.00),
    (4, 1, 'Required', 4, 1.50),
    (4, 9, 'Required', 4, 1.50),
    (4, 10, 'Required', 3, 1.30),
    (5, 1, 'Required', 3, 1.30),
    (5, 7, 'Required', 3, 1.50),
    (5, 8, 'Preferred', 2, 1.00),
    (6, 1, 'Required', 3, 1.20),
    (6, 7, 'Required', 3, 1.50),
    (6, 15, 'Required', 4, 1.50),
    (7, 11, 'Required', 3, 1.50),
    (7, 12, 'Required', 3, 1.50),
    (7, 13, 'Preferred', 3, 1.00),
    (8, 1, 'Required', 3, 1.50),
    (8, 7, 'Preferred', 2, 1.00),
    (8, 13, 'Preferred', 2, 1.00);
-- ============================================================
-- 12. APPLICATIONS
-- ============================================================
INSERT INTO applications (
        application_id,
        student_id,
        internship_id,
        resume_reference,
        cover_letter,
        match_score,
        status
    )
VALUES (
        1,
        2,
        1,
        'resumes/aarav.pdf',
        'Interested in full stack development.',
        88.50,
        'Shortlisted'
    ),
    (
        2,
        2,
        5,
        'resumes/aarav.pdf',
        'Interested in backend engineering.',
        85.00,
        'Applied'
    ),
    (
        3,
        3,
        2,
        'resumes/ananya.pdf',
        'Interested in machine learning.',
        95.00,
        'Interview'
    ),
    (
        4,
        3,
        4,
        'resumes/ananya.pdf',
        'Interested in AI research.',
        91.00,
        'Shortlisted'
    ),
    (
        5,
        4,
        5,
        'resumes/rahul.pdf',
        'Interested in database development.',
        87.00,
        'Applied'
    ),
    (
        6,
        5,
        6,
        'resumes/priya.pdf',
        'Interested in data analytics.',
        93.00,
        'Shortlisted'
    ),
    (
        7,
        5,
        2,
        'resumes/priya.pdf',
        'Interested in machine learning.',
        76.00,
        'Under Review'
    ),
    (
        8,
        6,
        3,
        'resumes/arjun.pdf',
        'Interested in cloud engineering.',
        90.00,
        'Interview'
    ),
    (
        9,
        6,
        7,
        'resumes/arjun.pdf',
        'Interested in DevOps.',
        94.00,
        'Applied'
    ),
    (
        10,
        7,
        8,
        'resumes/sneha.pdf',
        'Interested in Python development.',
        89.00,
        'Applied'
    );
-- ============================================================
-- 13. APPLICATION STATUS HISTORY
-- ============================================================
INSERT INTO application_status_history (
        application_id,
        changed_by,
        old_status,
        new_status,
        remarks
    )
VALUES (
        1,
        8,
        'Applied',
        'Shortlisted',
        'Good technical profile.'
    ),
    (
        3,
        9,
        'Applied',
        'Under Review',
        'Application reviewed.'
    ),
    (
        3,
        9,
        'Under Review',
        'Interview',
        'Selected for interview.'
    ),
    (
        4,
        11,
        'Applied',
        'Shortlisted',
        'Strong AI background.'
    ),
    (
        6,
        9,
        'Applied',
        'Shortlisted',
        'Good analytical skills.'
    ),
    (
        8,
        10,
        'Applied',
        'Under Review',
        'Cloud experience reviewed.'
    ),
    (
        8,
        10,
        'Under Review',
        'Interview',
        'Interview scheduled.'
    );
-- ============================================================
-- 14. INTERVIEWS
-- ============================================================
INSERT INTO interviews (
        interview_id,
        application_id,
        scheduled_by,
        interview_round,
        scheduled_at,
        mode,
        meeting_link,
        status,
        remarks
    )
VALUES (
        1,
        3,
        9,
        'Technical Round',
        '2026-12-05 10:00:00',
        'Online',
        'https://example.com/meeting1',
        'Scheduled',
        'Machine learning technical interview.'
    ),
    (
        2,
        8,
        10,
        'Technical Round',
        '2026-12-07 11:00:00',
        'Online',
        'https://example.com/meeting2',
        'Scheduled',
        'Cloud engineering interview.'
    ),
    (
        3,
        1,
        8,
        'HR Round',
        '2026-12-08 14:00:00',
        'Online',
        'https://example.com/meeting3',
        'Scheduled',
        'HR discussion.'
    ),
    (
        4,
        6,
        9,
        'Technical Round',
        '2026-12-09 15:00:00',
        'Offline',
        NULL,
        'Scheduled',
        'Data analytics interview.'
    );
-- ============================================================
-- 15. INTERVIEW EVALUATIONS
-- ============================================================
INSERT INTO interview_evaluations (
        interview_id,
        technical_score,
        communication_score,
        problem_solving_score,
        overall_score,
        comments,
        recommendation
    )
VALUES (
        1,
        9,
        8,
        9,
        88.00,
        'Strong machine learning knowledge.',
        'Select'
    ),
    (
        2,
        8,
        8,
        9,
        85.00,
        'Good understanding of cloud concepts.',
        'Review'
    );
-- ============================================================
-- 16. STUDENT PREFERENCES
-- ============================================================
INSERT INTO student_preferences (
        student_id,
        preferred_domain,
        preferred_location,
        preferred_work_mode,
        minimum_stipend,
        preferred_duration
    )
VALUES (
        2,
        'Software Development',
        'Bengaluru',
        'Hybrid',
        10000,
        3
    ),
    (
        3,
        'Artificial Intelligence',
        'Hyderabad',
        'Remote',
        15000,
        6
    ),
    (
        4,
        'Backend Development',
        'Bengaluru',
        'Hybrid',
        10000,
        3
    ),
    (
        5,
        'Data Analytics',
        'Hyderabad',
        'Remote',
        12000,
        3
    ),
    (
        6,
        'Cloud Computing',
        'Bengaluru',
        'On-site',
        15000,
        4
    ),
    (
        7,
        'Software Development',
        'Pune',
        'Hybrid',
        10000,
        3
    );
-- ============================================================
-- 17. SAVED INTERNSHIPS
-- ============================================================
INSERT INTO saved_internships (student_id, internship_id)
VALUES (2, 1),
    (2, 5),
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8);
-- ============================================================
-- 18. FEEDBACK
-- ============================================================
INSERT INTO feedback (
        application_id,
        submitted_by,
        rating,
        comments,
        feedback_type
    )
VALUES (
        1,
        2,
        5,
        'The application process was smooth.',
        'Student'
    ),
    (
        3,
        3,
        4,
        'Good communication from recruiter.',
        'Student'
    ),
    (
        6,
        9,
        5,
        'Strong candidate profile.',
        'Recruiter'
    ),
    (
        8,
        10,
        4,
        'Good technical background.',
        'Recruiter'
    );
-- ============================================================
-- RESET SERIAL SEQUENCES
-- ============================================================
SELECT setval(
        pg_get_serial_sequence('roles', 'role_id'),
        (
            SELECT MAX(role_id)
            FROM roles
        )
    );
SELECT setval(
        pg_get_serial_sequence('users', 'user_id'),
        (
            SELECT MAX(user_id)
            FROM users
        )
    );
SELECT setval(
        pg_get_serial_sequence('companies', 'company_id'),
        (
            SELECT MAX(company_id)
            FROM companies
        )
    );
SELECT setval(
        pg_get_serial_sequence('skills', 'skill_id'),
        (
            SELECT MAX(skill_id)
            FROM skills
        )
    );
SELECT setval(
        pg_get_serial_sequence('student_projects', 'project_id'),
        (
            SELECT MAX(project_id)
            FROM student_projects
        )
    );
SELECT setval(
        pg_get_serial_sequence('internships', 'internship_id'),
        (
            SELECT MAX(internship_id)
            FROM internships
        )
    );
SELECT setval(
        pg_get_serial_sequence('applications', 'application_id'),
        (
            SELECT MAX(application_id)
            FROM applications
        )
    );
SELECT setval(
        pg_get_serial_sequence('interviews', 'interview_id'),
        (
            SELECT MAX(interview_id)
            FROM interviews
        )
    );
SELECT setval(
        pg_get_serial_sequence('interview_evaluations', 'evaluation_id'),
        (
            SELECT MAX(evaluation_id)
            FROM interview_evaluations
        )
    );
SELECT setval(
        pg_get_serial_sequence('student_preferences', 'preference_id'),
        (
            SELECT MAX(preference_id)
            FROM student_preferences
        )
    );
SELECT setval(
        pg_get_serial_sequence('saved_internships', 'saved_id'),
        (
            SELECT MAX(saved_id)
            FROM saved_internships
        )
    );
SELECT setval(
        pg_get_serial_sequence('feedback', 'feedback_id'),
        (
            SELECT MAX(feedback_id)
            FROM feedback
        )
    );
COMMIT;
-- ============================================================
-- END OF SAMPLE DATA
-- ============================================================