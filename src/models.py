from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    CSV = "csv"
    RESUME_TXT = "resume_txt"
    RESUME_PDF = "resume_pdf"


class MissingValueStrategy(str, Enum):
    NULL = "null"
    OMIT = "omit"
    ERROR = "error"


class FieldProvenance(BaseModel):
    source: SourceType
    source_file: str
    confidence: float = Field(ge=0.0, le=1.0)
    raw_value: str


class Skill(BaseModel):
    name: str
    canonical_name: str
    provenance: list[FieldProvenance] = []


class ContactInfo(BaseModel):
    email: Optional[str] = None
    email_provenance: list[FieldProvenance] = []
    phone: Optional[str] = None
    phone_provenance: list[FieldProvenance] = []


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None


class Candidate(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    name_provenance: list[FieldProvenance] = []
    contact: ContactInfo = Field(default_factory=ContactInfo)
    skills: list[Skill] = []
    experience: list[Experience] = []
    education: list[Education] = []
    summary: Optional[str] = None
    summary_provenance: list[FieldProvenance] = []


class OutputConfig(BaseModel):
    fields: list[str] = Field(default_factory=lambda: [f.value for f in OutputField])
    field_rename: dict[str, str] = {}
    include_confidence: bool = True
    missing_value: MissingValueStrategy = MissingValueStrategy.NULL


class OutputField(str, Enum):
    CANDIDATE_ID = "candidate_id"
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SUMMARY = "summary"
