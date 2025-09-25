from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dep
    PdfReader = None  # type: ignore


def extract_pdf_text(path: str | Path) -> List[Dict[str, str]]:
    """Extracts per-page text into a list of {page, text} dicts.

    Falls back to empty if dependency is not available.
    """
    p = Path(path)
    if not p.exists() or PdfReader is None:
        return []
    reader = PdfReader(str(p))
    pages: List[Dict[str, str]] = []
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        pages.append({"page": str(i + 1), "text": txt})
    return pages


