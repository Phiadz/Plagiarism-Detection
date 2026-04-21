from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Lowercase and collapse extra whitespace for consistent matching."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text