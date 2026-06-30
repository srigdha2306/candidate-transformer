from __future__ import annotations
from src.models import Candidate, Skill, FieldProvenance


def merge_candidates(candidates: list[Candidate]) -> Candidate:
    if not candidates:
        raise ValueError("No candidates to merge")

    primary = candidates[0]
    for other in candidates[1:]:
        _merge_name(primary, other)
        _merge_contact(primary, other)
        _merge_skills(primary, other)
        _merge_experience(primary, other)
        _merge_education(primary, other)
        _merge_summary(primary, other)

    return primary


def _merge_name(primary: Candidate, other: Candidate) -> None:
    if not primary.name and other.name:
        primary.name = other.name
        primary.name_provenance.extend(other.name_provenance)
    elif primary.name and other.name and primary.name != other.name:
        primary.name_provenance.extend(other.name_provenance)


def _merge_contact(primary: Candidate, other: Candidate) -> None:
    if not primary.contact.email and other.contact.email:
        primary.contact.email = other.contact.email
        primary.contact.email_provenance.extend(other.contact.email_provenance)
    elif other.contact.email:
        primary.contact.email_provenance.extend(other.contact.email_provenance)

    if not primary.contact.phone and other.contact.phone:
        primary.contact.phone = other.contact.phone
        primary.contact.phone_provenance.extend(other.contact.phone_provenance)
    elif other.contact.phone:
        primary.contact.phone_provenance.extend(other.contact.phone_provenance)


def _merge_skills(primary: Candidate, other: Candidate) -> None:
    existing_canonical = {s.canonical_name for s in primary.skills}
    for skill in other.skills:
        if skill.canonical_name in existing_canonical:
            existing = next(s for s in primary.skills if s.canonical_name == skill.canonical_name)
            existing.provenance.extend(skill.provenance)
        else:
            primary.skills.append(skill)
            existing_canonical.add(skill.canonical_name)


def _merge_experience(primary: Candidate, other: Candidate) -> None:
    for exp in other.experience:
        primary.experience.append(exp)


def _merge_education(primary: Candidate, other: Candidate) -> None:
    for edu in other.education:
        primary.education.append(edu)


def _merge_summary(primary: Candidate, other: Candidate) -> None:
    if not primary.summary and other.summary:
        primary.summary = other.summary
        primary.summary_provenance.extend(other.summary_provenance)
    elif other.summary:
        primary.summary_provenance.extend(other.summary_provenance)
