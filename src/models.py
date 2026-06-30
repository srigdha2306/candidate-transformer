from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
import re


class SourceType(str, Enum):
    CSV = "csv"
    RESUME = "resume"
    LINKEDIN = "linkedin"


class MissingValueStrategy(str, Enum):
    NULL = "null"
    OMIT = "omit"
    ERROR = "error"


class ScoredField(BaseModel):
    value: Any
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[SourceType] = None


class Email(ScoredField):
    value: str

    @field_validator("value")
    @classmethod
    def validate_email(cls, v: str) -> str:
        import re
        v = v.lower().strip()
        if "@" not in v:
            raise ValueError(f"Invalid email: {v}")
        local, domain = v.rsplit("@", 1)
        if not local or not domain:
            raise ValueError(f"Invalid email: {v}")
        if "." not in domain:
            raise ValueError(f"Invalid email: {v}")
        parts = domain.split(".")
        if any(len(p) == 0 for p in parts):
            raise ValueError(f"Invalid email: {v}")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError(f"Invalid email: {v}")
        return v


class Phone(ScoredField):
    value: str


class Skill(BaseModel):
    name: str
    canonical_name: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[SourceType] = None


class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    raw: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[SourceType] = None


class Link(BaseModel):
    url: str
    type: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[SourceType] = None


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[SourceType] = None


class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    description: Optional[str] = None
    year: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[SourceType] = None


class Candidate(BaseModel):
    candidate_id: str
    full_name: Optional[str] = None
    emails: list[Email] = []
    phones: list[Phone] = []
    location: Optional[Location] = None
    links: list[Link] = []
    headline: Optional[str] = None
    years_experience: Optional[int] = None
    skills: list[Skill] = []
    experience: list[Experience] = []
    education: list[Education] = []
    provenance: dict[str, str] = {}
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class OutputConfig(BaseModel):
    fields: Optional[list[str]] = None
    field_rename: dict[str, str] = {}
    include_confidence: bool = True
    missing_value: MissingValueStrategy = MissingValueStrategy.NULL
    default_region: str = "IN"


class OutputField(str, Enum):
    CANDIDATE_ID = "candidate_id"
    FULL_NAME = "full_name"
    EMAILS = "emails"
    PHONES = "phones"
    LOCATION = "location"
    LINKS = "links"
    HEADLINE = "headline"
    YEARS_EXPERIENCE = "years_experience"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROVENANCE = "provenance"
    OVERALL_CONFIDENCE = "overall_confidence"
