from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

from app.utils.calib import parse_kitti_calib


def project_points_to_image(points_xyz: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Project 3D points (Nx3) to image plane using 3x4 projection matrix P.
    Returns Nx2 pixel coordinates (no filtering/clipping here).
    """
    n = points_xyz.shape[0]
    homog = np.hstack([points_xyz, np.ones((n, 1), dtype=points_xyz.dtype)])  # Nx4
    pix_h = homog @ P.T  # Nx3
    pix = pix_h[:, :2] / np.clip(pix_h[:, 2:3], 1e-6, None)
    return pix


def load_kitti_and_project(base_dir: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Skeleton utility: returns (points_xyz, pixels_xy)."""
    calib = parse_kitti_calib(base_dir / "calib.txt")
    P = calib.get("P2")  # typical camera projection
    if P is None:
        P = np.eye(3, 4, dtype=float)
    # Placeholder: generate a few fake points
    points = np.array([[1.0, 0.0, 5.0], [0.0, 0.0, 10.0], [2.0, -1.0, 8.0]])
    pixels = project_points_to_image(points, P)
    return points, pixels
