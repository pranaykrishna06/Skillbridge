# SkillBridge Frontend (replacement)

This is a replacement for the `frontend/` directory in the supplied SkillBridge repository.

## Requirements
- Node.js 20.9 or newer
- FastAPI backend running at `http://localhost:8000`
- PostgreSQL and Neo4j configured for the backend

## Setup
1. Replace the existing repository `frontend/` directory with this directory.
2. From this directory, create `.env.local`:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Install and run:

   ```bash
   npm install
   npm run dev
   ```
4. Open http://localhost:3000.

## Included integration
- Login: `POST /api/auth/login`, then `GET /api/auth/me`
- Registration: `POST /api/auth/register`, followed by login
- Student profile, internship discovery, applications, saved internships, recommendations
- Recruiter company onboarding, internship creation, applicant review/status changes
- JWT bearer token added to authenticated API calls

## Important backend limitations
- Registration creates the account only. After registering, students must complete their academic profile and recruiters must register a company before using role-specific features.
- The current backend has no complete admin-management API, so the admin dashboard intentionally reports that limitation instead of displaying fake controls.
- Student skill creation requires a valid `skill_id`; this frontend does not invent skill IDs. Add skills after connecting a skills-catalog endpoint or selecting IDs from your database.
- This frontend is wired to the endpoints present in the supplied backend. Optional endpoints can still return errors if their database tables, seed records, or external services are not configured.

## Notes
- Existing Next.js 16 / React 19 project dependencies are retained.
- `.env.local` is intentionally not included; configure it on each machine.
- Never commit real secrets or production credentials.
