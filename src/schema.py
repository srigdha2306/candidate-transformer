OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
        "full_name": {"type": ["string", "null"]},
        "emails": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "confidence": {"type": "number"},
                            "source": {"type": "string"},
                        },
                        "required": ["value"],
                    },
                ]
            },
        },
        "phones": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "confidence": {"type": "number"},
                            "source": {"type": "string"},
                        },
                        "required": ["value"],
                    },
                ]
            },
        },
        "location": {
            "oneOf": [
                {"type": "object", "properties": {
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "country": {"type": "string"},
                }},
                {"type": "null"},
            ],
        },
        "links": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "type": {"type": "string"},
                        },
                        "required": ["url"],
                    },
                ]
            },
        },
        "headline": {"type": ["string", "null"]},
        "years_experience": {"type": ["integer", "null"]},
        "skills": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "canonical_name": {"type": "string"},
                            "confidence": {"type": "number"},
                            "source": {"type": "string"},
                        },
                        "required": ["name", "canonical_name"],
                    },
                ]
            },
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "description": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "duration": {"type": "string"},
                },
            },
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": "string"},
                    "institution": {"type": "string"},
                    "description": {"type": "string"},
                    "year": {"type": "string"},
                },
            },
        },
        "provenance": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "overall_confidence": {"type": "number"},
    },
    "required": ["candidate_id"],
}
