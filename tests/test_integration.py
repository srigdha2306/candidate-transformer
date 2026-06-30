import json
from pathlib import Path
from src.config import load_config
from src.extractors.csv_extractor import extract_from_csv
from src.extractors.resume_extractor import extract_from_resume
from src.merger import merge_candidates
from src.exporter import export_candidate


class TestIntegration:
    def test_csv_only(self, tmp_path):
        csv_file = tmp_path / "candidates.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,555-123-4567,Python; SQL"
        )
        config = load_config("config.json")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        assert result["candidate_id"] == "C001"
        assert result["name"]["value"] == "Alice"

    def test_csv_and_resume_merge(self, tmp_path):
        csv_file = tmp_path / "candidates.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,555-123-4567,Python; SQL\n"
        )
        resume_file = tmp_path / "resume.txt"
        resume_file.write_text(
            "Alice Johnson\nalice@test.com\n555-123-4567\nSkills: Docker, Kubernetes"
        )
        config = load_config("config.json")
        csv_candidates = extract_from_csv(csv_file)
        resume_candidate = extract_from_resume(resume_file)
        all_candidates = csv_candidates + ([resume_candidate] if resume_candidate else [])
        merged = merge_candidates(all_candidates)
        result = export_candidate(merged, config)
        assert result["candidate_id"] == "C001"
        skill_names = [s["canonical_name"] for s in result["skills"]]
        assert "Python" in skill_names
        assert "Docker" in skill_names
        assert "Kubernetes" in skill_names

    def test_omit_missing_values(self, tmp_path):
        config = load_config("config.json")
        config.missing_value = "omit"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("candidate_id,name\nC001,Alice")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        assert "summary" not in result

    def test_output_schema_valid(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,+15551234567,Python"
        )
        config = load_config("config.json")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        phone_val = result["phone"]
        if isinstance(phone_val, dict):
            phone_val = phone_val["value"]
        assert phone_val.startswith("+")
