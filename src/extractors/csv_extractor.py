from __future__ import annotations
import csv
import re
import logging
from pathlib import Path
from src.models import Candidate, SourceType, Email, Phone, Skill, Experience, Education
from src.normalizers import normalize_email, normalize_phone, normalize_skill

logger = logging.getLogger(__name__)


def extract_from_csv(path: str | Path, default_region: str = "IN") -> list[Candidate]:
    path = Path(path)
    candidates: dict[str, Candidate] = {}

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("candidate_id", "").strip()
            if not cid:
                continue

            if cid not in candidates:
                candidates[cid] = Candidate(candidate_id=cid)

            candidate = candidates[cid]

            def _get(key: str) -> str:
                val = row.get(key)
                return val.strip() if val else ""

            raw_name = _get("name")
            if raw_name and not candidate.full_name:
                candidate.full_name = raw_name
                _merge_provenance(candidate, "full_name", "csv")

            raw_email = _get("email")
            if raw_email:
                norm = normalize_email(raw_email)
                val = norm or raw_email
                candidate.emails.append(Email(value=val, confidence=0.9, source=SourceType.CSV))
                _merge_provenance(candidate, "emails", "csv")

            raw_phone = _get("phone")
            if raw_phone:
                norm = normalize_phone(raw_phone, default_region)
                val = norm or raw_phone
                candidate.phones.append(Phone(value=val, confidence=0.9, source=SourceType.CSV))
                _merge_provenance(candidate, "phones", "csv")

            raw_skills = _get("skills")
            if raw_skills:
                for skill_name in [s.strip() for s in re.split(r"[;,]", raw_skills) if s.strip()]:
                    raw_key, canonical = normalize_skill(skill_name)
                    existing = next((s for s in candidate.skills if s.canonical_name == canonical), None)
                    if existing:
                        existing.confidence = max(existing.confidence, 0.9)
                    else:
                        candidate.skills.append(
                            Skill(name=skill_name, canonical_name=canonical, confidence=0.9, source=SourceType.CSV)
                        )
                    _merge_provenance(candidate, "skills", "csv")

            raw_title = _get("title")
            raw_company = _get("company")
            raw_description = _get("description")
            if raw_title or raw_company:
                candidate.experience.append(
                    Experience(
                        title=raw_title or None,
                        company=raw_company or None,
                        description=raw_description or None,
                        confidence=0.9,
                        source=SourceType.CSV,
                    )
                )
                _merge_provenance(candidate, "experience", "csv")

            raw_degree = _get("degree")
            raw_institution = _get("institution")
            if raw_degree or raw_institution:
                candidate.education.append(
                    Education(
                        degree=raw_degree or None,
                        institution=raw_institution or None,
                        confidence=0.9,
                        source=SourceType.CSV,
                    )
                )
                _merge_provenance(candidate, "education", "csv")

    return list(candidates.values())


def _merge_provenance(candidate: Candidate, field: str, source: str) -> None:
    existing = candidate.provenance.get(field, "")
    sources = {s.strip() for s in existing.split(",") if s.strip()}
    sources.add(source)
    candidate.provenance[field] = ",".join(sorted(sources))
