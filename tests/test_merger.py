from src.models import Candidate, Skill, ContactInfo, FieldProvenance, SourceType
from src.merger import merge_candidates


def _make_prov(source, val):
    return FieldProvenance(
        source=SourceType.CSV,
        source_file="test.csv",
        confidence=0.9,
        raw_value=val,
    )


class TestMerger:
    def test_merge_name_from_second(self):
        c1 = Candidate(candidate_id="C001")
        c2 = Candidate(candidate_id="C001", name="Alice")
        c2.name_provenance.append(_make_prov("csv", "Alice"))
        merged = merge_candidates([c1, c2])
        assert merged.name == "Alice"

    def test_merge_skills_deduplicates(self):
        c1 = Candidate(candidate_id="C001")
        c1.skills.append(Skill(name="Python", canonical_name="Python"))
        c2 = Candidate(candidate_id="C001")
        c2.skills.append(Skill(name="Python", canonical_name="Python"))
        c2.skills.append(Skill(name="Docker", canonical_name="Docker"))
        merged = merge_candidates([c1, c2])
        names = [s.canonical_name for s in merged.skills]
        assert names == ["Python", "Docker"]

    def test_merge_email_fills_gap(self):
        c1 = Candidate(candidate_id="C001")
        c2 = Candidate(candidate_id="C001")
        c2.contact.email = "alice@test.com"
        merged = merge_candidates([c1, c2])
        assert merged.contact.email == "alice@test.com"

    def test_raise_on_empty(self):
        try:
            merge_candidates([])
            assert False, "Should have raised"
        except ValueError:
            pass
