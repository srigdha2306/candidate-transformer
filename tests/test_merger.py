from src.models import Candidate, Skill, Email, Phone, SourceType
from src.merger import merge_candidates


def _make_candidate(cid: str, full_name: str | None = None) -> Candidate:
    c = Candidate(candidate_id=cid)
    if full_name:
        c.full_name = full_name
        c.provenance["full_name"] = "csv"
    return c


class TestMerger:
    def test_merge_name_from_second(self):
        c1 = _make_candidate("C001")
        c2 = _make_candidate("C001", "Alice")
        merged = merge_candidates([c1, c2])
        assert merged.full_name == "Alice"

    def test_csv_priority_over_resume(self):
        c_csv = _make_candidate("C001", "Alice Smith")
        c_csv.provenance["full_name"] = "csv"
        c_resume = _make_candidate("C001", "Alice")
        c_resume.provenance["full_name"] = "resume"
        merged = merge_candidates([c_csv, c_resume])
        assert merged.full_name == "Alice Smith"

    def test_merge_skills_deduplicates(self):
        c1 = _make_candidate("C001")
        c1.skills.append(Skill(name="Python", canonical_name="Python"))
        c2 = _make_candidate("C001")
        c2.skills.append(Skill(name="Python", canonical_name="Python"))
        c2.skills.append(Skill(name="Docker", canonical_name="Docker"))
        merged = merge_candidates([c1, c2])
        names = [s.canonical_name for s in merged.skills]
        assert names == ["Python", "Docker"]

    def test_merge_emails_combined(self):
        c1 = _make_candidate("C001")
        c1.emails.append(Email(value="alice@work.com"))
        c2 = _make_candidate("C001")
        c2.emails.append(Email(value="alice@personal.com"))
        merged = merge_candidates([c1, c2])
        assert len(merged.emails) == 2

    def test_merge_phones_dedup(self):
        c1 = _make_candidate("C001")
        c1.phones.append(Phone(value="+919876543210"))
        c2 = _make_candidate("C001")
        c2.phones.append(Phone(value="+919876543210"))
        merged = merge_candidates([c1, c2])
        assert len(merged.phones) == 1

    def test_merge_provenance_combined(self):
        c1 = _make_candidate("C001")
        c1.provenance = {"skills": "csv"}
        c2 = _make_candidate("C001")
        c2.provenance = {"skills": "resume"}
        merged = merge_candidates([c1, c2])
        sources = {s.strip() for s in merged.provenance["skills"].split(",")}
        assert sources == {"csv", "resume"}

    def test_raise_on_empty(self):
        try:
            merge_candidates([])
            assert False, "Should have raised"
        except ValueError:
            pass
