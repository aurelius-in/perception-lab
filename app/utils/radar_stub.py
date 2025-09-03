from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


def load_radar_csv(path: Path) -> List[Tuple[float, float, float]]:
    """Load a tiny CSV of radar points (x,y,v). Placeholder parser."""
    if not path.exists():
        return []
    pts: List[Tuple[float, float, float]] = []
    for line in path.read_text().splitlines():
        parts = [p for p in line.strip().split(",") if p]
        if len(parts) < 3:
            continue
        try:
            x, y, v = float(parts[0]), float(parts[1]), float(parts[2])
            pts.append((x, y, v))
        except ValueError:
            continue
    return pts
