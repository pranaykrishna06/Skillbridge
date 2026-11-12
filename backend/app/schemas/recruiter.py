from pydantic import BaseModel, Field
from typing import Optional


class CompanyCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    registration_number: str = Field(min_length=2, max_length=50)
    industry: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    designation: str = Field(min_length=2, max_length=100)


class CompanyUpdate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    industry: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None


class RecruiterUpdate(BaseModel):
    designation: str = Field(min_length=2, max_length=100)
