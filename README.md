# Multi-Source Candidate Data Transformer

A Python CLI tool that ingests candidate data from multiple sources (recruiter CSV, resume TXT/PDF), normalizes it, merges it with provenance tracking, and outputs canonical JSON.

## Architecture

```
CSV ──────────────────┐
                      │
                      ▼
                 ┌─────────┐
                 │ Extract │
                 └─────────┘
                      │
Resume ───────────────┤
(TXT/PDF)             │
                      ▼
                 ┌───────────┐
                 │ Normalize │  (email, phone, skill canonicalization)
                 └───────────┘
                      │
                      ▼
                 ┌─────────┐
                 │  Merge   │  CSV > Resume > LinkedIn priority
                 └─────────┘
                      │
                      ▼
                 ┌───────────┐
                 │ Validate  │  (email, phone, required fields, dates)
                 └───────────┘
                      │
                      ▼
                 ┌─────────┐
                 │  JSON    │  (with provenance, confidence)
                 └─────────┘
```

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
    ├── test_integration.py
    ├── test_invalid_email.py
    ├── test_duplicate_skills.py
    ├── test_missing_phone.py
    └── test_merge_conflict.py
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

# Verbose logging
python -m src.cli -c sample_inputs/recruiter.csv -v
```

## Configuration

`config.json` supports:

| Field | Type | Default | Description |
|---|---|---|---|
| `fields` | `list[str]` | all fields | Output fields to include |
| `field_rename` | `dict` | `{}` | Rename output fields (e.g. `{"full_name": "name"}`) |
| `include_confidence` | `bool` | `true` | When `false`, strips confidence/source from output |
| `missing_value` | `"null" \| "omit" \| "error"` | `"null"` | How to handle missing values |
| `default_region` | `str` | `"IN"` | Default region for phone normalization |

### Example configs

```json
{
  "fields": ["candidate_id", "full_name", "emails", "skills"],
  "field_rename": { "candidate_id": "id", "full_name": "name" },
  "include_confidence": false,
  "missing_value": "omit",
  "default_region": "US"
}
```

## Output Schema

```json
{
  "candidate_id": "C001",
  "full_name": "Alice Smith",
  "emails": [{ "value": "alice@example.com", "confidence": 0.95, "source": "csv" }],
  "phones": [{ "value": "+919876543210", "confidence": 0.9, "source": "csv" }],
  "location": { "city": "Bangalore", "country": "India" },
  "links": [{ "url": "https://linkedin.com/in/alice", "type": "linkedin" }],
  "headline": "Senior Software Engineer",
  "years_experience": 8,
  "skills": [{ "name": "Python", "canonical_name": "Python", "confidence": 0.9, "source": "csv" }],
  "experience": [{ "title": "Engineer", "company": "Acme", "description": "Built things" }],
  "education": [{ "degree": "BS CS", "institution": "MIT", "description": "Computer Science" }],
  "provenance": { "full_name": "csv", "emails": "csv", "skills": "csv,resume" },
  "overall_confidence": 0.85
}
```

## Normalization

- **Email**: Lowercased, syntax-validated via `email-validator`
- **Phone**: Converted to E.164 format (`+919876543210`) via `phonenumbers` (default region `IN`, configurable)
- **Skills**: Mapped to canonical names (e.g., `js` → `JavaScript`, `k8s` → `Kubernetes`)

## Data Merging

When the same candidate appears across multiple sources:

| Field | Strategy |
|---|---|
| **full_name** | First non-null from highest-priority source (CSV > Resume > LinkedIn) |
| **emails / phones** | Appended, deduplicated by value |
| **skills** | Deduplicated by canonical_name, confidences merged (max) |
| **experience / education** | Appended from all sources |
| **provenance** | Merged across all sources (comma-separated) |
| **overall_confidence** | Recomputed as mean of all field confidences |

### Priority

1. **CSV** (highest, confidence 0.9)
2. **Resume** (confidence 0.7)
3. **LinkedIn** (lowest, confidence 0.5)

## Validation

- **Email**: Syntax validation via `email-validator` + Pydantic model validator
- **Phone**: E.164 format validation via `phonenumbers`
- **Skills**: Deduplicated by canonical name during merge
- **Missing required fields**: Configurable via `missing_value` strategy
- **Output schema**: Validated against JSON Schema on export

## Testing

```bash
pytest tests/ -v
```
