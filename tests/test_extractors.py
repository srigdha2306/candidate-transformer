import pytest
from pathlib import Path
from src.extractors.csv_extractor import extract_from_csv
from src.extractors.resume_extractor import extract_from_resume
from src.models import SourceType


class TestCsvExtractor:
    def test_extract_single_candidate(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,9876543210,Python"
        )
        candidates = extract_from_csv(csv_file)
        assert len(candidates) == 1
        assert candidates[0].candidate_id == "C001"
        assert candidates[0].full_name == "Alice"

    def test_extract_multiple_candidates(self, tmp_path):
        csv_file = tmp_path / "multi.csv"
        csv_file.write_text(
            "candidate_id,name,email\n"
            "C001,Alice,alice@test.com\n"
            "C002,Bob,bob@test.com"
        )
        candidates = extract_from_csv(csv_file)
        assert len(candidates) == 2

    def test_merge_rows_same_candidate(self, tmp_path):
        csv_file = tmp_path / "merge.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,,Python\n"
            "C001,,,9876543210,Docker"
        )
        candidates = extract_from_csv(csv_file)
        assert len(candidates) == 1
        c = candidates[0]
        assert c.full_name == "Alice"
        assert any(p.value == "+919876543210" for p in c.phones)
        assert len(c.skills) == 2


class TestResumeExtractor:
    def test_extract_from_txt(self, tmp_path):
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text(
            "Alice Johnson\n"
            "Software Engineer\n"
            "alice@test.com\n"
            "9876543210\n\n"
            "Skills: Python, Docker\n\n"
            "Experience\nLed projects\n\n"
            "Education\nBS CS\n\n"
        )
        c = extract_from_resume(txt_file)
        assert c is not None
        assert c.full_name == "Alice Johnson"
        assert any(e.value == "alice@test.com" for e in c.emails)
        assert len(c.skills) >= 2

    def test_missing_file(self, tmp_path):
        c = extract_from_resume(tmp_path / "nope.txt")
        assert c is None

    def test_provenance_on_extract(self, tmp_path):
        txt_file = tmp_path / "provenance_test.txt"
        txt_file.write_text(
            "Bob\nbob@test.com\nSkills: Python\n\nExperience\nDev\n\nEducation\nMIT"
        )
        c = extract_from_resume(txt_file)
        assert c.provenance.get("full_name") == "resume"
        assert c.provenance.get("emails") == "resume"
        assert c.provenance.get("skills") == "resume"
