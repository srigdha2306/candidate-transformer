# Multi-Source Candidate Data Transformer

A Python CLI tool that ingests candidate data from multiple sources (recruiter CSV, resume TXT/PDF), normalizes it, merges it with provenance tracking, and outputs canonical JSON.

## Project Structure

```
candidate_transformer/
├── config.json              # Runtime configuration
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Package metadata
├── README.md
├── sample_inputs/
│   ├── recruiter.csv        # Example CSV input
│   └── resume.txt           # Example resume text input
├── sample_outputs/
│   └── candidate.json       # Example output
├── src/
│   ├── cli.py               # CLI entry point
│   ├── config.py            # Config loader
│   ├── exporter.py          # JSON export + schema validation
│   ├── merger.py            # Merge logic with provenance
│   ├── models.py            # Pydantic models
│   ├── normalizers.py       # Email/phone/skill normalization
│   ├── schema.py            # JSON Schema for output
│   └── extractors/
│       ├── csv_extractor.py        # CSV structured data extraction
│       └── resume_extractor.py     # TXT/PDF unstructured extraction
└── tests/
    ├── test_normalizers.py
    ├── test_extractors.py
    ├── test_merger.py
    └── test_integration.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage with CSV and resume
python -m src.cli --csv sample_inputs/recruiter.csv --resume sample_inputs/resume.txt --output output.json

# Custom config
python -m src.cli -c sample_inputs/recruiter.csv -r sample_inputs/resume.txt -cfg myconfig.json -o result.json

# Multiple resumes
python -m src.cli -c sample_inputs/recruiter.csv -r resume1.txt -r resume2.pdf
```

## Configuration

`config.json` supports:

| Field | Type | Default | Description |
|---|---|---|---|
| `fields` | `list[str]` | all fields | Output fields to include |
| `field_rename` | `dict` | `{}` | Rename output fields |
| `include_confidence` | `bool` | `true` | Include provenance/confidence |
| `missing_value` | `"null" \| "omit" \| "error"` | `"null"` | How to handle missing values |

### Example configs

```json
{
  "fields": ["candidate_id", "name", "email", "skills"],
  "field_rename": { "candidate_id": "id" },
  "include_confidence": false,
  "missing_value": "omit"
}
```

## Normalization

- **Email**: Lowercased, syntax-validated via `email-validator`
- **Phone**: Converted to E.164 format (`+15551234567`) via `phonenumbers`
- **Skills**: Mapped to canonical names (e.g., `js` → `JavaScript`, `k8s` → `Kubernetes`)

## Data Merging

When the same candidate appears across multiple sources:
- **Name**: First non-null value wins, all provenances tracked
- **Email/Phone**: First non-null value wins, all provenances tracked
- **Skills**: Deduplicated by canonical name, provenances merged
- **Experience/Education**: Appended from all sources

## Testing

```bash
pytest tests/ -v
```
