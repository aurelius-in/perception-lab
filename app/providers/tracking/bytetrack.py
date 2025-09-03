from __future__ import annotations

from typing import List, Dict


class SimpleTracker:
    """Very basic deterministic tracker stub assigning incremental IDs."""

    def __init__(self) -> None:
        self._next_id = 1
        self._history: dict[int, list[tuple[int, int]]] = {}

    def update(self, boxes: List[Dict]) -> List[Dict]:
        tracks: List[Dict] = []
        for b in boxes:
            tid = self._next_id
            cx = int((b["x1"] + b["x2"]) / 2)
            cy = int((b["y1"] + b["y2"]) / 2)
            hist = self._history.setdefault(tid, [])
            hist.append((cx, cy))
            if len(hist) > 10:
                hist.pop(0)
            tracks.append({
                "id": tid,
                "cls": b.get("cls", "obj"),
                "x1": b["x1"], "y1": b["y1"], "x2": b["x2"], "y2": b["y2"],
                "trail": hist.copy(),
            })
            self._next_id += 1
        return tracks


