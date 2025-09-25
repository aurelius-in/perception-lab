from __future__ import annotations

from typing import Dict, Iterable, List


def section_by_pages(pages: List[Dict[str, str]], max_tokens: int = 1000) -> List[Dict[str, str]]:
    """Simple structure-aware-ish chunking: one chunk per page for now.

    Token budget is a placeholder; real tokenization would require a tokenizer.
    """
    chunks: List[Dict[str, str]] = []
    for entry in pages:
        text = entry.get("text", "")
        if not text:
            continue
        chunks.append({"title": f"Page {entry.get('page','?')}", "text": text})
    return chunks


