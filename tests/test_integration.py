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
            "C001,Alice,alice@test.com,9876543210,Python; SQL"
        )
        config = load_config("config.json")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        assert result["candidate_id"] == "C001"
        assert result["full_name"] == "Alice"

    def test_csv_and_resume_merge(self, tmp_path):
        csv_file = tmp_path / "candidates.csv"
        csv_file.write_text(
            "candidate_id,name,email,phone,skills\n"
            "C001,Alice,alice@test.com,9876543210,Python; SQL"
        )
        resume_file = tmp_path / "resume.txt"
        resume_file.write_text(
            "Alice Johnson\nalice@test.com\nSkills: Docker, Kubernetes"
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
        assert result["overall_confidence"] > 0

    def test_omit_missing_values(self, tmp_path):
        config = load_config("config.json")
        config.missing_value = "omit"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("candidate_id,name\nC001,Alice")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        assert "location" not in result

    def test_include_confidence_false(self, tmp_path):
        config = load_config("config.json")
        config.include_confidence = False
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("candidate_id,name,email\nC001,Alice,alice@test.com")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        assert isinstance(result["emails"][0], str)
        assert isinstance(result["skills"], list)

    def test_field_rename(self, tmp_path):
        config = load_config("config.json")
        config.field_rename = {"candidate_id": "id", "full_name": "name"}
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("candidate_id,name\nC001,Alice")
        candidates = extract_from_csv(csv_file)
        merged = merge_candidates(candidates)
        result = export_candidate(merged, config)
        assert "id" in result
        assert result["name"] == "Alice"
        assert "candidate_id" not in result
