# Run SkillBridge without Docker (Windows + macOS)

This project uses **two development terminals**:
- Terminal A: FastAPI backend (`http://localhost:8000`)
- Terminal B: Next.js frontend (`http://localhost:3000`)

PostgreSQL and Neo4j run as native local services in the background. Docker is not used.

## Required local software

1. Python 3.11
2. Node.js 20.9 or newer (LTS recommended)
3. PostgreSQL 16 with the `pgvector` extension
4. Neo4j Community 5.x (or Neo4j Desktop with a local DBMS)

The databases are required by this codebase. This bundle does not replace PostgreSQL/Neo4j with SQLite or an in-memory mock.

## A. Install and start PostgreSQL

### Windows
1. Install PostgreSQL 16 using the official Windows installer: https://www.postgresql.org/download/windows/
2. Remember the password you set for the `postgres` user.
3. Install the matching `pgvector` extension for your PostgreSQL version using the pgvector Windows installation instructions: https://github.com/pgvector/pgvector
4. Ensure the PostgreSQL service is running (Windows Services -> postgresql-x64-16).

### macOS (Homebrew)
```bash
brew install postgresql@16
brew services start postgresql@16
```
Install pgvector for that PostgreSQL installation:
```bash
brew install pgvector
```
If PostgreSQL was installed from a different source, follow the pgvector instructions for that exact installation.

## B. Install and start Neo4j

Install Neo4j Community or Neo4j Desktop: https://neo4j.com/download/

Create/start a local database with:
- Bolt URI: `bolt://localhost:7687`
- Username: `neo4j`
- Password: choose one and remember it

For Neo4j Desktop, create a local DBMS, set its password, start it, and confirm Bolt is listening on port 7687. Neo4j runs as a background service/application; it does not need a development terminal.

## C. Create the PostgreSQL database (one time)

Open a terminal at the project root.

### Windows PowerShell
Ensure PostgreSQL's `bin` directory is in PATH (typically `C:\Program Files\PostgreSQL\16\bin`), then:
```powershell
createdb -U postgres skillbridge
psql -U postgres -d skillbridge -f database/schema.sql
psql -U postgres -d skillbridge -f database/seed.sql
```

### macOS
```bash
createdb skillbridge
psql -d skillbridge -f database/schema.sql
psql -d skillbridge -f database/seed.sql
```

If `createdb` says the database already exists, do not run the schema or seed again. The schema is not a migration and the seed is intended for a fresh database.

If `CREATE EXTENSION vector` fails, pgvector is not installed for the PostgreSQL server you are using. Install the matching extension before retrying on a fresh database.

## D. Configure backend environment

Copy `backend/.env.example` to `backend/.env` and edit:
- `DATABASE_URL` with your PostgreSQL username/password
- `NEO4J_PASSWORD` with the Neo4j password you selected
- `JWT_SECRET_KEY` with a long random secret

Example:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/skillbridge
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_NEO4J_PASSWORD
JWT_SECRET_KEY=use_a_long_random_secret_value_at_least_32_chars
```

Do not commit `backend/.env`.

## E. Start in exactly two development terminals

### Terminal 1 — backend
Windows: double-click `START_BACKEND_WINDOWS.bat`, or run it from PowerShell:
```powershell
.\START_BACKEND_WINDOWS.bat
```
macOS:
```bash
chmod +x START_BACKEND_MAC_LINUX.sh
./START_BACKEND_MAC_LINUX.sh
```

First run creates a Python virtual environment and installs dependencies. PyTorch and the sentence-transformer model can take time and disk space to download. The embedding model may download the first time an embedding feature is used.

### Terminal 2 — frontend
Windows:
```powershell
.\START_FRONTEND_WINDOWS.bat
```
macOS:
```bash
chmod +x START_FRONTEND_MAC_LINUX.sh
./START_FRONTEND_MAC_LINUX.sh
```

Open http://localhost:3000

Backend API docs: http://localhost:8000/docs

## F. Verify connections

After both servers start:
- http://localhost:8000/health
- http://localhost:8000/health/postgres
- http://localhost:8000/health/neo4j

Both database health endpoints must report `connected`. If either fails, check that its native database service is running and that the credentials/ports in `backend/.env` are correct.

## Demo accounts
All seeded accounts use password: `SkillBridge@123`
- Admin: `admin@skillbridge.com`
- Student: `aarav@gmail.com`
- Recruiter: `karan@techsolutions.com`

## Notes / honest limitations
- This is a local-development setup, not a production deployment.
- You must install PostgreSQL + pgvector and Neo4j locally; avoiding Docker does not remove the database requirements.
- First-time Python dependency installation is large because the project uses PyTorch and sentence-transformers.
- The startup scripts start the two application servers; PostgreSQL and Neo4j must already be installed and running as native services.
- Do not share your `.env` file or commit real passwords.
