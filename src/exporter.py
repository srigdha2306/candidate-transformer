from __future__ import annotations
import json
import logging
from typing import Any
from jsonschema import validate, ValidationError
from src.models import Candidate, OutputConfig, MissingValueStrategy, OutputField

logger = logging.getLogger(__name__)


def export_candidate(candidate: Candidate, config: OutputConfig) -> dict:
    has_rename = bool(config.field_rename)
    data = _build_output(candidate, config)
    _validate_output(data, skip=has_rename)
    return data


def _build_output(candidate: Candidate, config: OutputConfig) -> dict:
    out = {}
    field_set = set(config.fields) if config.fields else {f.value for f in OutputField}

    for field in OutputField:
        if field.value not in field_set:
            continue
        value = _get_field_value(candidate, field, config)
        if value is None and config.missing_value == MissingValueStrategy.OMIT:
            continue
        if value is None and config.missing_value == MissingValueStrategy.ERROR:
            raise ValueError(f"Missing required field: {field.value}")

        out_name = config.field_rename.get(field.value, field.value)
        out[out_name] = value

    return out


def _get_field_value(candidate: Candidate, field: OutputField, config: OutputConfig) -> Any:
    include_conf = config.include_confidence

    if field == OutputField.CANDIDATE_ID:
        return candidate.candidate_id

    if field == OutputField.FULL_NAME:
        return _scalar_or_conf(candidate.full_name, None, None, include_conf)

    if field == OutputField.EMAILS:
        if not candidate.emails:
            return []
        return [_scored_to_output(e, include_conf) for e in candidate.emails]

    if field == OutputField.PHONES:
        if not candidate.phones:
            return []
        return [_scored_to_output(p, include_conf) for p in candidate.phones]

    if field == OutputField.LOCATION:
        if candidate.location is None:
            return None
        loc = candidate.location
        out = {}
        if loc.city:
            out["city"] = loc.city
        if loc.state:
            out["state"] = loc.state
        if loc.country:
            out["country"] = loc.country
        if loc.raw and not (loc.city or loc.state or loc.country):
            out["raw"] = loc.raw
        if include_conf:
            out["confidence"] = loc.confidence
            if loc.source:
                out["source"] = loc.source.value
        return out if out else None

    if field == OutputField.LINKS:
        if not candidate.links:
            return []
        return [_scored_to_output(l, include_conf) for l in candidate.links]

    if field == OutputField.HEADLINE:
        return _scalar_or_conf(candidate.headline, None, None, include_conf)

    if field == OutputField.YEARS_EXPERIENCE:
        return candidate.years_experience

    if field == OutputField.SKILLS:
        if not candidate.skills:
            return []
        result = []
        for s in candidate.skills:
            entry = {"name": s.name, "canonical_name": s.canonical_name}
            if include_conf:
                entry["confidence"] = s.confidence
                if s.source:
                    entry["source"] = s.source.value
            result.append(entry)
        return result

    if field == OutputField.EXPERIENCE:
        if not candidate.experience:
            return []
        result = []
        for e in candidate.experience:
            entry = {}
            for attr in ("title", "company", "description", "start_date", "end_date", "duration"):
                val = getattr(e, attr, None)
                if val is not None:
                    entry[attr] = val
            if include_conf:
                entry["confidence"] = e.confidence
                if e.source:
                    entry["source"] = e.source.value
            result.append(entry)
        return result

    if field == OutputField.EDUCATION:
        if not candidate.education:
            return []
        result = []
        for e in candidate.education:
            entry = {}
            for attr in ("degree", "institution", "description", "year"):
                val = getattr(e, attr, None)
                if val is not None:
                    entry[attr] = val
            if include_conf:
                entry["confidence"] = e.confidence
                if e.source:
                    entry["source"] = e.source.value
            result.append(entry)
        return result

    if field == OutputField.PROVENANCE:
        return candidate.provenance if candidate.provenance else {}

    if field == OutputField.OVERALL_CONFIDENCE:
        return candidate.overall_confidence

    return None


def _scalar_or_conf(value: Any, confidence: float | None, source: str | None, include_conf: bool) -> Any:
    if value is None:
        return None
    if not include_conf or (confidence is None and source is None):
        return value
    out = {"value": value}
    if confidence is not None:
        out["confidence"] = confidence
    if source is not None:
        out["source"] = source
    return out


def _scored_to_output(obj: Any, include_conf: bool) -> Any:
    if obj is None:
        return None
    if not include_conf:
        return _get_primary_value(obj)
    out = {}
    primary = _get_primary_value(obj)
    if primary is not None:
        out["value"] = primary
    if hasattr(obj, "confidence") and obj.confidence is not None:
        out["confidence"] = obj.confidence
    if hasattr(obj, "source") and obj.source is not None:
        out["source"] = obj.source.value if hasattr(obj.source, "value") else str(obj.source)
    return out


def _get_primary_value(obj: Any) -> Any:
    if hasattr(obj, "value"):
        return obj.value
    if hasattr(obj, "url"):
        return obj.url
    return str(obj)


def _validate_output(data: dict, skip: bool = False) -> None:
    if skip:
        return
    from src.schema import OUTPUT_SCHEMA
    try:
        validate(instance=data, schema=OUTPUT_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Output validation failed: {e.message}")
