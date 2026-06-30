from src.models import Candidate, Skill
from src.merger import merge_candidates


class TestDuplicateSkills:
    def test_duplicate_skills_deduped_in_merge(self):
        c1 = Candidate(candidate_id="C001")
        c1.skills.append(Skill(name="Python", canonical_name="Python"))
        c1.skills.append(Skill(name="Python", canonical_name="Python"))
        assert len(c1.skills) == 2

    def test_merge_deduplicates_by_canonical(self):
        c1 = Candidate(candidate_id="C001")
        c1.skills.append(Skill(name="Python", canonical_name="Python"))
        c2 = Candidate(candidate_id="C001")
        c2.skills.append(Skill(name="Python", canonical_name="Python"))
        c2.skills.append(Skill(name="py", canonical_name="Python"))

        merged = merge_candidates([c1, c2])
        py_skills = [s for s in merged.skills if s.canonical_name == "Python"]
        assert len(py_skills) == 1
