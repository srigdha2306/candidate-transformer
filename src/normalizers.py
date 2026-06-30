from __future__ import annotations
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError

CANONICAL_SKILLS = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "gcp": "Google Cloud",
    "azure": "Azure",
    "git": "Git",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "FastAPI",
    "html": "HTML",
    "css": "CSS",
    "c++": "C++",
    "c#": "C#",
    "go": "Go",
    "rust": "Rust",
    "rest": "REST API",
    "rest api": "REST API",
    "graphql": "GraphQL",
    "redis": "Redis",
    "kafka": "Kafka",
    "terraform": "Terraform",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
}


def normalize_email(raw: str) -> str | None:
    raw = raw.strip().lower()
    try:
        result = validate_email(raw, check_deliverability=False)
        return result.normalized
    except EmailNotValidError:
        return None


def normalize_phone(raw: str, default_region: str = "IN") -> str | None:
    raw = raw.strip()
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass

    country_code = _default_country_code(default_region)
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"+{country_code}{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"+{digits[1:]}"
    if len(digits) > 11 and raw.startswith("+"):
        return raw
    return None


def _default_country_code(region: str) -> str:
    mapping = {
        "US": "1", "GB": "44", "IN": "91", "CA": "1",
        "AU": "61", "DE": "49", "FR": "33", "JP": "81",
        "SG": "65", "AE": "971",
    }
    return mapping.get(region.upper(), "91")


def normalize_skill(raw: str) -> tuple[str, str]:
    key = raw.strip().lower()
    canonical = CANONICAL_SKILLS.get(key)
    if canonical:
        return key, canonical
    return key, raw.strip()


def extract_skills_from_text(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for key in CANONICAL_SKILLS:
        pattern = re.compile(r"\b" + re.escape(key) + r"\b", re.IGNORECASE)
        if pattern.search(text_lower):
            found.append(key)
    return found
