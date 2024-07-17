
"""API test class."""

from faker import Faker
from cts_api.client import CtsApi

class TestApi:
    """API test."""
    fake = Faker()
    token = str(fake.uuid4())

    def test_api_init(self):
        """Test initializer."""
        cts_api = CtsApi(self.token, None)
        assert cts_api.token == self.token
