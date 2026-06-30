from __future__ import annotations
import logging
from src.models import Candidate, SourceType

logger = logging.getLogger(__name__)

SOURCE_PRIORITY = {
    SourceType.CSV: 3,
    SourceType.RESUME: 2,
    SourceType.LINKEDIN: 1,
}


def merge_candidates(candidates: list[Candidate]) -> Candidate:
    """
    Merge multiple Candidate objects into one.

    Priority order (highest wins): CSV > Resume > LinkedIn
    - Fields with higher-priority sources take precedence.
    - List fields (emails, phones, skills, experience, education) are appended.
    - Skills are deduplicated by canonical_name (highest-priority source retains the value).
    - Provenance is merged across all sources.
    - Overall confidence is recomputed as the mean of all field confidences.
    """
    if not candidates:
        raise ValueError("No candidates to merge")

    merged = candidates[0]
    for other in candidates[1:]:
        _merge_field(merged, other, "full_name")
        _merge_emails(merged, other)
        _merge_phones(merged, other)
        _merge_location(merged, other)
        _merge_links(merged, other)
        _merge_field(merged, other, "headline")
        _merge_years_experience(merged, other)
        _merge_skills(merged, other)
        _merge_list_field(merged, other, "experience")
        _merge_list_field(merged, other, "education")
        _merge_provenance(merged, other)

    _recompute_confidence(merged)
    return merged


def _priority(source_is: SourceType | None) -> int:
    if source_is is None:
        return 0
    return SOURCE_PRIORITY.get(source_is, 0)


def _merge_field(merged: Candidate, other: Candidate, field: str) -> None:
    """Merge a scalar field. Higher-priority source wins."""
    my_val = getattr(merged, field, None)
    other_val = getattr(other, field, None)
    if other_val is None:
        return
    if my_val is None:
        setattr(merged, field, other_val)
        if f"{field}_source" in merged.model_fields_set:
            pass
        return

    source_field = f"{field}_source"
    my_source = getattr(merged, source_field, None) if hasattr(merged, source_field) else None
    other_source = getattr(other, source_field, None) if hasattr(other, source_field) else None

    if _priority(other_source) > _priority(my_source):
        setattr(merged, field, other_val)


def _merge_emails(merged: Candidate, other: Candidate) -> None:
    existing_values = {e.value for e in merged.emails}
    for email in other.emails:
        if email.value not in existing_values:
            merged.emails.append(email)
            existing_values.add(email.value)


def _merge_phones(merged: Candidate, other: Candidate) -> None:
    existing_values = {p.value for p in merged.phones}
    for phone in other.phones:
        if phone.value not in existing_values:
            merged.phones.append(phone)
            existing_values.add(phone.value)


def _merge_location(merged: Candidate, other: Candidate) -> None:
    if merged.location is None:
        merged.location = other.location
        return
    if other.location is None:
        return
    if _priority(other.location.source) > _priority(merged.location.source):
        merged.location = other.location


def _merge_links(merged: Candidate, other: Candidate) -> None:
    existing_urls = {l.url for l in merged.links}
    for link in other.links:
        if link.url not in existing_urls:
            merged.links.append(link)
            existing_urls.add(link.url)


def _merge_years_experience(merged: Candidate, other: Candidate) -> None:
    if merged.years_experience is None and other.years_experience is not None:
        merged.years_experience = other.years_experience
    elif other.years_experience is not None:
        merged.years_experience = max(merged.years_experience or 0, other.years_experience)


def _merge_skills(merged: Candidate, other: Candidate) -> None:
    existing = {s.canonical_name for s in merged.skills}
    for skill in other.skills:
        if skill.canonical_name in existing:
            existing_skill = next(s for s in merged.skills if s.canonical_name == skill.canonical_name)
            existing_skill.confidence = max(existing_skill.confidence, skill.confidence)
        else:
            merged.skills.append(skill)
            existing.add(skill.canonical_name)


def _merge_list_field(merged: Candidate, other: Candidate, field: str) -> None:
    my_list = getattr(merged, field, [])
    other_list = getattr(other, field, [])
    my_list.extend(other_list)


def _merge_provenance(merged: Candidate, other: Candidate) -> None:
    for field, source_str in other.provenance.items():
        other_sources = {s.strip() for s in source_str.split(",") if s.strip()}
        existing = merged.provenance.get(field, "")
        merged_sources = {s.strip() for s in existing.split(",") if s.strip()}
        merged_sources.update(other_sources)
        merged.provenance[field] = ",".join(sorted(merged_sources))


def _recompute_confidence(merged: Candidate) -> None:
    confidences = []

    if merged.full_name:
        confidences.append(0.7)

    confidences.extend(e.confidence for e in merged.emails)
    confidences.extend(p.confidence for p in merged.phones)
    confidences.extend(s.confidence for s in merged.skills)
    confidences.extend(e.confidence for e in merged.experience)
    confidences.extend(e.confidence for e in merged.education)

    if merged.location:
        confidences.append(merged.location.confidence)

    if not confidences:
        merged.overall_confidence = 0.0
    else:
        merged.overall_confidence = round(sum(confidences) / len(confidences), 2)
