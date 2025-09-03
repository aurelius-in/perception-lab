from __future__ import annotations

from typing import List, Dict


class SimpleTracker:
    """Very basic deterministic tracker stub assigning incremental IDs."""

    def __init__(self) -> None:
        self._next_id = 1

    def update(self, boxes: List[Dict]) -> List[Dict]:
        tracks: List[Dict] = []
        for b in boxes:
            tracks.append({
                "id": self._next_id,
                "cls": b.get("cls", "obj"),
                "x1": b["x1"], "y1": b["y1"], "x2": b["x2"], "y2": b["y2"],
            })
            self._next_id += 1
        return tracks


