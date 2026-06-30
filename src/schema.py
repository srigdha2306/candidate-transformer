OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
        "name": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "provenance": {"type": "array"},
                    },
                    "required": ["value"],
                },
            ]
        },
        "email": {
            "oneOf": [
                {"type": "string"},
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "provenance": {"type": "array"},
                    },
                    "required": ["value"],
                },
            ]
        },
        "phone": {
            "oneOf": [
                {"type": "string"},
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "provenance": {"type": "array"},
                    },
                    "required": ["value"],
                },
            ]
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "canonical_name": {"type": "string"},
                    "provenance": {"type": "array"},
                },
                "required": ["name", "canonical_name"],
            },
        },
        "experience": {
            "oneOf": [
                {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "description": {"type": "string"},
                    },
                }},
                {"type": "null"},
            ],
        },
        "education": {
            "oneOf": [
                {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "degree": {"type": "string"},
                        "institution": {"type": "string"},
                    },
                }},
                {"type": "null"},
            ],
        },
        "summary": {
            "oneOf": [
                {"type": "string"},
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "provenance": {"type": "array"},
                    },
                    "required": ["value"],
                },
            ]
        },
    },
    "required": ["candidate_id"],
}
