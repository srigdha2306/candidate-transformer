from __future__ import annotations
import json
from jsonschema import validate, ValidationError
from src.models import Candidate, OutputConfig, MissingValueStrategy, OutputField


def export_candidate(candidate: Candidate, config: OutputConfig) -> dict:
    data = _build_output(candidate, config)
    _validate_output(data)
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


def _get_field_value(candidate: Candidate, field: OutputField, config: OutputConfig) -> object | None:
    include_conf = config.include_confidence

    if field == OutputField.CANDIDATE_ID:
        return candidate.candidate_id
    if field == OutputField.NAME:
        if candidate.name is None:
            return None
        if include_conf and candidate.name_provenance:
            return {
                "value": candidate.name,
                "provenance": [p.model_dump() for p in candidate.name_provenance],
            }
        return candidate.name
    if field == OutputField.EMAIL:
        if candidate.contact.email is None:
            return None
        if include_conf and candidate.contact.email_provenance:
            return {
                "value": candidate.contact.email,
                "provenance": [p.model_dump() for p in candidate.contact.email_provenance],
            }
        return candidate.contact.email
    if field == OutputField.PHONE:
        if candidate.contact.phone is None:
            return None
        if include_conf and candidate.contact.phone_provenance:
            return {
                "value": candidate.contact.phone,
                "provenance": [p.model_dump() for p in candidate.contact.phone_provenance],
            }
        return candidate.contact.phone
    if field == OutputField.SKILLS:
        if not candidate.skills:
            return None if config.missing_value == MissingValueStrategy.NULL else []
        result = []
        for s in candidate.skills:
            entry = {"name": s.name, "canonical_name": s.canonical_name}
            if include_conf and s.provenance:
                entry["provenance"] = [p.model_dump() for p in s.provenance]
            result.append(entry)
        return result
    if field == OutputField.EXPERIENCE:
        if not candidate.experience:
            return None if config.missing_value == MissingValueStrategy.NULL else []
        return [e.model_dump(exclude_none=True) for e in candidate.experience]
    if field == OutputField.EDUCATION:
        if not candidate.education:
            return None if config.missing_value == MissingValueStrategy.NULL else []
        return [e.model_dump(exclude_none=True) for e in candidate.education]
    if field == OutputField.SUMMARY:
        if candidate.summary is None:
            return None
        if include_conf and candidate.summary_provenance:
            return {
                "value": candidate.summary,
                "provenance": [p.model_dump() for p in candidate.summary_provenance],
            }
        return candidate.summary
    return None


def _validate_output(data: dict) -> None:
    from src.schema import OUTPUT_SCHEMA
    try:
        validate(instance=data, schema=OUTPUT_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Output validation failed: {e.message}")
