from __future__ import annotations

import base64
from pathlib import Path


def read_file_bytes(path: str | Path) -> bytes:
    return Path(path).read_bytes()


def to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def from_b64(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


