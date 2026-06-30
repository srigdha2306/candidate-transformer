from src.models import Candidate, SourceType
from src.merger import merge_candidates


class TestMergeConflict:
    def test_csv_wins_over_resume_for_name(self):
        csv_candidate = Candidate(candidate_id="C001", full_name="Alice Smith")
        csv_candidate.provenance["full_name"] = "csv"
        resume_candidate = Candidate(candidate_id="C001", full_name="Alice Johnson")
        resume_candidate.provenance["full_name"] = "resume"

        merged = merge_candidates([csv_candidate, resume_candidate])
        assert merged.full_name == "Alice Smith"

    def test_resume_wins_over_linkedin_for_name(self):
        resume_candidate = Candidate(candidate_id="C001", full_name="Alice Resume")
        resume_candidate.provenance["full_name"] = "resume"
        linkedin_candidate = Candidate(candidate_id="C001", full_name="Alice LI")
        linkedin_candidate.provenance["full_name"] = "linkedin"

        merged = merge_candidates([resume_candidate, linkedin_candidate])
        assert merged.full_name == "Alice Resume"

    def test_provenance_merges_across_conflicts(self):
        c1 = Candidate(candidate_id="C001", full_name="Alice")
        c1.provenance = {"skills": "csv"}
        c2 = Candidate(candidate_id="C001", full_name="Alice")
        c2.provenance = {"skills": "resume", "education": "linkedin"}

        merged = merge_candidates([c1, c2])
        skill_sources = {s.strip() for s in merged.provenance["skills"].split(",")}
        assert skill_sources == {"csv", "resume"}
        edu_sources = {s.strip() for s in merged.provenance["education"].split(",")}
        assert edu_sources == {"linkedin"}

    def test_experience_appended_from_all_sources(self):
        c1 = Candidate(candidate_id="C001")

        from src.models import Experience
        c1.experience.append(Experience(title="Engineer A", company="Company X", source=SourceType.CSV))
        c2 = Candidate(candidate_id="C001")
        c2.experience.append(Experience(title="Engineer B", company="Company Y", source=SourceType.RESUME))

        merged = merge_candidates([c1, c2])
        assert len(merged.experience) == 2

    def test_overall_confidence_computed(self):
        c1 = Candidate(candidate_id="C001", full_name="Alice")
        from src.models import Email, Skill
        c1.emails.append(Email(value="a@b.com", confidence=0.9))
        c1.skills.append(Skill(name="Python", canonical_name="Python", confidence=0.8))

        merged = merge_candidates([c1])
        assert merged.overall_confidence > 0
        assert merged.overall_confidence <= 1.0
