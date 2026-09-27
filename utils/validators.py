"""URL validation and sanitization for video sources."""

from __future__ import annotations

import re
from urllib.parse import urlparse

# Regex patterns matching standard TikTok web URLs and shortlinks (vm.tiktok.com, vt.tiktok.com)
TIKTOK_PATTERNS = [
    r"^https?://(?:www\.|m\.)?tiktok\.com/@[\w.\-]+/video/\d+",
    r"^https?://(?:www\.|m\.)?tiktok\.com/v/\d+",
    r"^https?://(?:vm|vt)\.tiktok\.com/[\w\-]+",
    r"^https?://(?:www\.)?tiktok\.com/t/[\w\-]+",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in TIKTOK_PATTERNS]


def is_valid_tiktok_url(url: str) -> bool:
    """Validate whether the given string is a valid public TikTok URL."""
    if not url or not isinstance(url, str):
        return False
    
    clean = url.strip()
    if not clean.startswith(("http://", "https://")):
        return False

    parsed = urlparse(clean)
    domain = parsed.netloc.lower()
    
    # Quick domain pre-check
    valid_domains = ("tiktok.com", "www.tiktok.com", "m.tiktok.com", "vm.tiktok.com", "vt.tiktok.com")
    if not any(domain == vd or domain.endswith("." + vd) for vd in valid_domains):
        return False

    return any(pattern.match(clean) for pattern in COMPILED_PATTERNS)


def sanitize_url(url: str) -> str:
    """Clean up and trim input URL string."""
    if not url:
        return ""
    return url.strip()
