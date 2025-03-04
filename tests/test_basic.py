"""
Basic tests for CF-Ares.
"""

import pytest

from cf_ares import AresClient


def test_client_initialization():
    """Test that the client can be initialized."""
    client = AresClient()
    assert client is not None
    client.close()


def test_client_with_context_manager():
    """Test that the client can be used with a context manager."""
    with AresClient() as client:
        assert client is not None


@pytest.mark.skip(reason="Requires internet connection and may hit rate limits")
def test_get_request():
    """Test that a GET request can be made."""
    with AresClient() as client:
        response = client.get("https://httpbin.org/get")
        assert response.status_code == 200
        assert response.json()


@pytest.mark.skip(reason="Requires internet connection and may hit rate limits")
def test_post_request():
    """Test that a POST request can be made."""
    with AresClient() as client:
        response = client.post(
            "https://httpbin.org/post",
            json={"key": "value"},
        )
        assert response.status_code == 200
        assert response.json()["json"]["key"] == "value"


@pytest.mark.skip(reason="Requires Cloudflare protected site")
def test_cloudflare_bypass():
    """Test that Cloudflare can be bypassed."""
    with AresClient(browser_engine="undetected", headless=False) as client:
        # Replace with a known Cloudflare-protected site
        response = client.get("https://example.com")
        assert response.status_code == 200
        assert "Cloudflare" not in response.text 