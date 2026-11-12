from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class InternshipCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str

    work_mode: str
    location: Optional[str] = None

    stipend: float = Field(ge=0)
    duration_months: int = Field(ge=1, le=24)
    available_positions: int = Field(gt=0)

    minimum_cgpa: float = Field(ge=0, le=10)
    minimum_year: int = Field(ge=1, le=6)

    application_deadline: date
    status: str = "Open"


class InternshipUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str

    work_mode: str
    location: Optional[str] = None

    stipend: float = Field(ge=0)
    duration_months: int = Field(ge=1, le=24)
    available_positions: int = Field(gt=0)

    minimum_cgpa: float = Field(ge=0, le=10)
    minimum_year: int = Field(ge=1, le=6)

    application_deadline: date

    status: str


class InternshipSkillCreate(BaseModel):
    skill_id: int
    requirement_type: str
    minimum_proficiency: int = Field(ge=1, le=5)
    importance_weight: float = Field(gt=0)
