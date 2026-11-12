from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes.internships import router as internship_router
from app.core.config import settings
from app.api.routes.health import router
from app.api.routes.auth import router as auth_router
from app.api.routes.students import router as student_router
from app.api.routes.recruiters import router as recruiter_router
from app.db.neo4j import close_neo4j_connection
from app.api.routes.applications import router as application_router
from app.api.routes.graph import router as graph_router
from app.api.routes.notifications import router as notifications_router
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_neo4j_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="Internship discovery, application tracking, and recruiter management platform",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(recruiter_router)
app.include_router(internship_router)
app.include_router(application_router)
app.include_router(graph_router)
app.include_router(notifications_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to SkillBridge API",
        "status": "running"
    }
