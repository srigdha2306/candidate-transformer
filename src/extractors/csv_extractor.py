from __future__ import annotations
import csv
from pathlib import Path
from src.models import Candidate, SourceType, FieldProvenance, Skill, ContactInfo, Experience, Education
from src.normalizers import normalize_email, normalize_phone, normalize_skill


def extract_from_csv(path: str | Path) -> list[Candidate]:
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
            prov = FieldProvenance(
                source=SourceType.CSV,
                source_file=str(path),
                confidence=0.9,
                raw_value="",
            )

            def _get(key: str) -> str:
                val = row.get(key)
                return val.strip() if val else ""

            raw_name = _get("name")
            if raw_name and not candidate.name:
                candidate.name = raw_name
                candidate.name_provenance.append(
                    FieldProvenance(**{**prov.model_dump(), "raw_value": raw_name})
                )

            raw_email = _get("email")
            if raw_email:
                norm_email = normalize_email(raw_email)
                candidate.contact.email = norm_email or raw_email
                candidate.contact.email_provenance.append(
                    FieldProvenance(**{**prov.model_dump(), "raw_value": raw_email})
                )

            raw_phone = _get("phone")
            if raw_phone:
                norm_phone = normalize_phone(raw_phone)
                candidate.contact.phone = norm_phone or raw_phone
                candidate.contact.phone_provenance.append(
                    FieldProvenance(**{**prov.model_dump(), "raw_value": raw_phone})
                )

            raw_skills = _get("skills")
            if raw_skills:
                import re
                for skill_name in [s.strip() for s in re.split(r"[;,]", raw_skills) if s.strip()]:
                    raw_key, canonical = normalize_skill(skill_name)
                    existing = next((s for s in candidate.skills if s.canonical_name == canonical), None)
                    if existing:
                        existing.provenance.append(
                            FieldProvenance(**{**prov.model_dump(), "raw_value": skill_name})
                        )
                    else:
                        candidate.skills.append(
                            Skill(
                                name=skill_name,
                                canonical_name=canonical,
                                provenance=[FieldProvenance(**{**prov.model_dump(), "raw_value": skill_name})],
                            )
                        )

            raw_title = _get("title")
            raw_company = _get("company")
            if raw_title or raw_company:
                candidate.experience.append(
                    Experience(
                        title=raw_title or None,
                        company=raw_company or None,
                    )
                )

            raw_degree = _get("degree")
            raw_institution = _get("institution")
            if raw_degree or raw_institution:
                candidate.education.append(
                    Education(
                        degree=raw_degree or None,
                        institution=raw_institution or None,
                    )
                )

    return list(candidates.values())
