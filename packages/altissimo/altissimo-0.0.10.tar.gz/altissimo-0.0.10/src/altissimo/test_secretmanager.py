"""Altissimo SecretManager Tests file."""
from .secretmanager import SecretManager


def test_get_secret():
    """Test the get_secret function."""
    s = SecretManager()
    assert s.get_secret("test-secret", project="altissimo-dev") == "test-secret-value"
