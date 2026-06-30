from __future__ import annotations
import re
import logging
from pathlib import Path
from src.models import Candidate, SourceType, Email, Phone, Skill, Experience, Education, Location
from src.normalizers import normalize_email, normalize_phone, normalize_skill, extract_skills_from_text

logger = logging.getLogger(__name__)


def extract_from_resume(path: str | Path, default_region: str = "IN") -> Candidate | None:
    path = Path(path)
    text = _read_file(path)
    if text is None:
        return None

    source_type = SourceType.RESUME

    cid = f"resume-{path.stem}"
    candidate = Candidate(candidate_id=cid)

    name = _extract_name(text)
    if name:
        candidate.full_name = name
        candidate.provenance["full_name"] = "resume"

    emails_raw = _extract_emails(text)
    for raw in emails_raw:
        norm = normalize_email(raw)
        if norm:
            candidate.emails.append(Email(value=norm, confidence=0.7, source=source_type))
            _merge_provenance(candidate, "emails", "resume")

    phones_raw = _extract_phones(text)
    for raw in phones_raw:
        norm = normalize_phone(raw, default_region)
        if norm:
            candidate.phones.append(Phone(value=norm, confidence=0.7, source=source_type))
            _merge_provenance(candidate, "phones", "resume")

    skill_keys = extract_skills_from_text(text)
    seen_canonical = set()
    for key in skill_keys:
        raw_key, canonical = normalize_skill(key)
        if canonical in seen_canonical:
            continue
        seen_canonical.add(canonical)
        candidate.skills.append(
            Skill(name=raw_key, canonical_name=canonical, confidence=0.7, source=source_type)
        )
        _merge_provenance(candidate, "skills", "resume")

    experiences = _extract_experience_sections(text)
    for exp in experiences:
        exp.source = source_type
        exp.confidence = 0.7
        candidate.experience.append(exp)
        _merge_provenance(candidate, "experience", "resume")

    educations = _extract_education_sections(text)
    for edu in educations:
        edu.source = source_type
        edu.confidence = 0.7
        candidate.education.append(edu)
        _merge_provenance(candidate, "education", "resume")

    headline = _extract_headline(text)
    if headline:
        candidate.headline = headline
        candidate.provenance["headline"] = "resume"

    location_raw = _extract_location(text)
    if location_raw:
        candidate.location = Location(raw=location_raw, confidence=0.5, source=source_type)
        candidate.provenance["location"] = "resume"

    _compute_overall_confidence(candidate)
    return candidate


def _merge_provenance(candidate: Candidate, field: str, source: str) -> None:
    existing = candidate.provenance.get(field, "")
    sources = {s.strip() for s in existing.split(",") if s.strip()}
    sources.add(source)
    candidate.provenance[field] = ",".join(sorted(sources))


def _compute_overall_confidence(candidate: Candidate) -> None:
    confidences = []

    if candidate.full_name:
        confidences.append(0.7)

    confidences.extend(e.confidence for e in candidate.emails)
    confidences.extend(p.confidence for p in candidate.phones)
    confidences.extend(s.confidence for s in candidate.skills)
    confidences.extend(e.confidence for e in candidate.experience)
    confidences.extend(e.confidence for e in candidate.education)

    if candidate.location:
        confidences.append(candidate.location.confidence)

    if not confidences:
        candidate.overall_confidence = 0.0
    else:
        candidate.overall_confidence = round(sum(confidences) / len(confidences), 2)


def _read_file(path: Path) -> str | None:
    if not path.exists():
        return None
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return path.read_text("utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        raise RuntimeError("PyPDF2 is required to read PDF files")


def _extract_name(text: str) -> str | None:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[0] if lines else None


def _extract_headline(text: str) -> str | None:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            continue
        line = line.strip()
        if line and len(line) < 120 and not re.match(r"^[\d\W]+$", line):
            keywords = ["engineer", "developer", "scientist", "analyst", "manager", "architect",
                        "intern", "lead", "specialist", "consultant"]
            if any(k in line.lower() for k in keywords):
                return line
    return None


def _extract_location(text: str) -> str | None:
    patterns = [
        r"(?:located\s+(?:in|at)\s+)?([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?)",
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            candidate = match.group(1).strip()
            if 3 < len(candidate) < 100:
                return candidate
    return None


def _extract_emails(text: str) -> list[str]:
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def _extract_phones(text: str) -> list[str]:
    pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    return re.findall(pattern, text)


def _extract_experience_sections(text: str) -> list[Experience]:
    experiences = []
    exp_patterns = [
        r"(?:Experience|Work Experience|Employment)(.*?)(?=(?:Education|Skills|Projects|Certifications|$))",
    ]
    for pat in exp_patterns:
        match = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if match:
            block = match.group(1).strip()
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            for line in lines[:3]:
                experiences.append(Experience(description=line if len(line) > 20 else None))
            break
    return experiences


def _extract_education_sections(text: str) -> list[Education]:
    educations = []
    edu_patterns = [
        r"(?:Education|Academic Background)(.*?)(?=(?:Experience|Skills|Projects|Certifications|$))",
    ]
    for pat in edu_patterns:
        match = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if match:
            block = match.group(1).strip()
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            for line in lines[:3]:
                educations.append(Education(description=line if len(line) > 10 else None))
            break
    return educations
