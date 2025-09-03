from __future__ import annotations

from typing import List, Tuple


def estimate_trajectory_stub(frames: List[bytes]) -> List[Tuple[float, float]]:
    """Placeholder VO trajectory; returns a small straight-line path."""
    return [(i * 1.0, 0.0) for i in range(min(len(frames), 10))]
