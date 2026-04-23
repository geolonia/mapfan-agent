import pytest
from mapfan_agent.client import MapfanClient


def test_client_headers_with_key():
    client = MapfanClient(api_url="http://localhost:8000", api_key="test-key")
    assert client._headers["X-API-Key"] == "test-key"
    assert client._headers["Content-Type"] == "application/json"


def test_client_headers_without_key():
    client = MapfanClient(api_url="http://localhost:8000")
    assert "X-API-Key" not in client._headers


def test_client_base_url():
    client = MapfanClient(api_url="http://localhost:8000")
    assert client._base_url == "http://localhost:8000/api/v1"


def test_client_base_url_strips_trailing_slash():
    client = MapfanClient(api_url="http://localhost:8000/")
    assert client._base_url == "http://localhost:8000/api/v1"
