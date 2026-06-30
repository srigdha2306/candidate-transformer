import pytest
from src.models import Email


class TestInvalidEmail:
    def test_email_validation_raises(self):
        with pytest.raises(ValueError):
            Email(value="not-an-email")

    def test_email_missing_at(self):
        with pytest.raises(ValueError):
            Email(value="userexample.com")

    def test_email_missing_domain(self):
        with pytest.raises(ValueError):
            Email(value="user@.com")

    def test_email_no_tld(self):
        with pytest.raises(ValueError):
            Email(value="user@example")

    def test_valid_email_passes(self):
        e = Email(value="user@example.com")
        assert e.value == "user@example.com"
