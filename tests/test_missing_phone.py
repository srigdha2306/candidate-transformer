from src.models import Candidate
from src.merger import merge_candidates


class TestMissingPhone:
    def test_missing_phone_ok(self):
        c = Candidate(candidate_id="C001", full_name="Alice")
        merged = merge_candidates([c])
        assert merged.phones == []

    def test_missing_phone_and_email(self):
        c = Candidate(candidate_id="C001", full_name="Bob")
        merged = merge_candidates([c])
        assert merged.phones == []
        assert merged.emails == []

    def test_phone_from_second_source(self):
        c1 = Candidate(candidate_id="C001")
        c2 = Candidate(candidate_id="C001")

        from src.models import Phone, SourceType
        c2.phones.append(Phone(value="+919876543210", source=SourceType.CSV))
        merged = merge_candidates([c1, c2])
        assert len(merged.phones) == 1
        assert merged.phones[0].value == "+919876543210"
