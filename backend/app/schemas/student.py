from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# Student Profile

class StudentProfileCreate(BaseModel):
    registration_number: str = Field(min_length=3, max_length=30)
    department: str = Field(min_length=2, max_length=100)
    year_of_study: int = Field(ge=1, le=6)
    cgpa: float = Field(ge=0, le=10)
    graduation_year: int = Field(ge=2024)
    bio: Optional[str] = None


class StudentProfileUpdate(BaseModel):
    registration_number: str = Field(min_length=3, max_length=30)
    department: str = Field(min_length=2, max_length=100)
    year_of_study: int = Field(ge=1, le=6)
    cgpa: float = Field(ge=0, le=10)
    graduation_year: int = Field(ge=2024)
    bio: Optional[str] = None


# Student Skills

class StudentSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int = Field(ge=1, le=5)
    years_experience: float = Field(ge=0)
    last_used_date: Optional[date] = None


# Student Projects

class StudentProjectCreate(BaseModel):
    project_title: str = Field(min_length=2, max_length=150)
    project_description: str
    project_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
