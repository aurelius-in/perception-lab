from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np


def parse_kitti_calib(path: Path) -> Dict[str, np.ndarray]:
    """Parse minimal KITTI calib file into name->numpy array."""
    mapping: Dict[str, np.ndarray] = {}
    if not path.exists():
        return mapping
    for line in path.read_text().splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        nums = [float(x) for x in val.strip().split()] if val.strip() else []
        arr = np.array(nums, dtype=float)
        # Heuristic: reshape to 3x4 if 12 entries
        if arr.size == 12:
            arr = arr.reshape(3, 4)
        mapping[key.strip()] = arr
    return mapping
