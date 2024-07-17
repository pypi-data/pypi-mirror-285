"""API integration tests."""

import os

import pytest

from cts_api.client import CtsApi

@pytest.mark.asyncio
async def test_lines_discovery_call():
    """lines-discovery test"""
    api_token = os.environ.get("CTS_API_TOKEN")
    assert api_token is not None, "API token must be set in the environment"

    cts_api = CtsApi(api_token, None)

    response = await cts_api.lines_discovery()

    assert response is not None
