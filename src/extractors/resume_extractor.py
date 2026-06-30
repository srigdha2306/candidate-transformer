from __future__ import annotations
import re
from pathlib import Path
from src.models import Candidate, SourceType, FieldProvenance, Skill, Experience, Education
from src.normalizers import normalize_email, normalize_phone, normalize_skill, extract_skills_from_text


def extract_from_resume(path: str | Path) -> Candidate | None:
    path = Path(path)
    text = _read_file(path)
    if text is None:
        return None

    source_type = SourceType.RESUME_PDF if path.suffix.lower() == ".pdf" else SourceType.RESUME_TXT

    prov = FieldProvenance(
        source=source_type,
        source_file=str(path),
        confidence=0.7,
        raw_value="",
    )

    cid = f"resume-{path.stem}"
    candidate = Candidate(candidate_id=cid)

    name = _extract_name(text)
    if name:
        candidate.name = name
        candidate.name_provenance.append(
            FieldProvenance(**{**prov.model_dump(), "raw_value": name})
        )

    emails = _extract_emails(text)
    if emails:
        norm = normalize_email(emails[0])
        candidate.contact.email = norm or emails[0]
        candidate.contact.email_provenance.append(
            FieldProvenance(**{**prov.model_dump(), "raw_value": emails[0]})
        )

    phones = _extract_phones(text)
    if phones:
        norm = normalize_phone(phones[0])
        candidate.contact.phone = norm or phones[0]
        candidate.contact.phone_provenance.append(
            FieldProvenance(**{**prov.model_dump(), "raw_value": phones[0]})
        )

    skill_keys = extract_skills_from_text(text)
    seen_canonical = set()
    for key in skill_keys:
        raw_key, canonical = normalize_skill(key)
        if canonical in seen_canonical:
            continue
        seen_canonical.add(canonical)
        candidate.skills.append(
            Skill(
                name=key,
                canonical_name=canonical,
                provenance=[FieldProvenance(**{**prov.model_dump(), "raw_value": key})],
            )
        )

    experiences = _extract_experience_sections(text)
    for exp in experiences:
        candidate.experience.append(exp)

    educations = _extract_education_sections(text)
    for edu in educations:
        candidate.education.append(edu)

    return candidate


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
