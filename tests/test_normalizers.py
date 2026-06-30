import pytest
from src.normalizers import normalize_email, normalize_phone, normalize_skill, extract_skills_from_text


class TestNormalizeEmail:
    def test_valid_email(self):
        assert normalize_email("Alice@Example.COM") == "alice@example.com"

    def test_invalid_email(self):
        assert normalize_email("not-an-email") is None

    def test_empty_string(self):
        assert normalize_email("") is None


class TestNormalizePhone:
    def test_in_phone_with_dashes(self):
        assert normalize_phone("98765-43210") == "+919876543210"

    def test_in_phone_no_prefix(self):
        assert normalize_phone("9876543210") == "+919876543210"

    def test_e164_already(self):
        assert normalize_phone("+919876543210") == "+919876543210"

    def test_us_phone_with_region_override(self):
        result = normalize_phone("555-123-4567", "US")
        assert result == "+15551234567"

    def test_international(self):
        result = normalize_phone("+44 20 7946 0958")
        assert result == "+442079460958"

    def test_garbage(self):
        assert normalize_phone("not-a-number") is None


class TestNormalizeSkill:
    def test_known_skill(self):
        raw, canonical = normalize_skill("Python")
        assert canonical == "Python"

    def test_known_aliased_skill(self):
        raw, canonical = normalize_skill("js")
        assert canonical == "JavaScript"

    def test_unknown_skill(self):
        raw, canonical = normalize_skill("COBOL")
        assert raw == "cobol"
        assert canonical == "COBOL"


class TestExtractSkillsFromText:
    def test_found_skills(self):
        text = "I know Python and Docker and KUBERNETES"
        found = extract_skills_from_text(text)
        assert "python" in found
        assert "docker" in found
        assert "kubernetes" in found

    def test_no_skills(self):
        text = "I like cooking and hiking"
        assert extract_skills_from_text(text) == []
