from pydantic import BaseModel, Field
from typing import Optional


class ApplicationCreate(BaseModel):
    internship_id: int
    resume_reference: Optional[str] = Field(default=None, max_length=255)
    cover_letter: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: str
    remarks: Optional[str] = None


class StudentPreferenceUpdate(BaseModel):
    preferred_domain: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_work_mode: Optional[str] = None
    minimum_stipend: float = Field(default=0, ge=0)
    preferred_duration: Optional[int] = Field(default=None, ge=1, le=24)
