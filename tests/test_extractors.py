import pytest
from pathlib import Path
from src.extractors.csv_extractor import extract_from_csv
from src.extractors.resume_extractor import extract_from_resume


class TestCsvExtractor:
    def test_extract_single_candidate(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,555-1234,Python"
        )
        candidates = extract_from_csv(csv_file)
        assert len(candidates) == 1
        assert candidates[0].candidate_id == "C001"
        assert candidates[0].name == "Alice"

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
            "C001,,,555-123-4567,Docker"
        )
        candidates = extract_from_csv(csv_file)
        assert len(candidates) == 1
        c = candidates[0]
        assert c.name == "Alice"
        assert c.contact.phone == "+15551234567"
        assert len(c.skills) == 2


class TestResumeExtractor:
    def test_extract_from_txt(self, tmp_path):
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text(
            "Alice Johnson\n"
            "alice@test.com\n"
            "555-123-4567\n\n"
            "Skills: Python, Docker\n\n"
            "Experience\nLed projects\n\n"
            "Education\nBS CS"
        )
        c = extract_from_resume(txt_file)
        assert c is not None
        assert c.name == "Alice Johnson"
        assert c.contact.email == "alice@test.com"
        assert len(c.skills) >= 2

    def test_missing_file(self, tmp_path):
        c = extract_from_resume(tmp_path / "nope.txt")
        assert c is None
