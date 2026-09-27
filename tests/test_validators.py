"""Unit tests for URL validation and sanitization."""

import pytest
from utils.validators import is_valid_tiktok_url, sanitize_url


def test_valid_tiktok_standard_urls():
    valid_urls = [
        "https://www.tiktok.com/@username/video/7123456789012345678",
        "http://www.tiktok.com/@creator.name/video/1234567890",
        "https://tiktok.com/@user_name-1/video/987654321012345",
        "https://m.tiktok.com/v/7123456789012345678.html",
        "https://vm.tiktok.com/ZM8eXqY4d/",
        "https://vt.tiktok.com/ZS8eXqY4d/",
        "https://www.tiktok.com/t/ZT8eXqY4d/",
    ]
    for url in valid_urls:
        assert is_valid_tiktok_url(url) is True, f"Failed for valid URL: {url}"


def test_invalid_urls():
    invalid_urls = [
        "",
        "not a url",
        "https://youtube.com/watch?v=12345",
        "https://instagram.com/reel/12345",
        "https://tiktok.com/",
        "https://tiktok.com/@username",
        "ftp://tiktok.com/@user/video/1234",
        "https://faketiktok.com/@user/video/1234",
    ]
    for url in invalid_urls:
        assert is_valid_tiktok_url(url) is False, f"Should be invalid: {url}"


def test_sanitize_url():
    assert sanitize_url("  https://www.tiktok.com/@user/video/123  \n") == "https://www.tiktok.com/@user/video/123"
    assert sanitize_url("") == ""
