from __future__ import annotations

import hashlib
import re
from typing import Tuple


def sha256_bytes(data: bytes) -> str:
    """Return hex sha256 of raw bytes."""
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


_ws_re = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Basic normalization: collapse whitespace and strip."""
    return _ws_re.sub(" ", text).strip()


def sha256_text_norm(text: str) -> Tuple[str, str]:
    """Return (normalized_text, sha256 hex)."""
    norm = normalize_text(text)
    return norm, sha256_bytes(norm.encode("utf-8"))


