from __future__ import annotations

from typing import List, Tuple

import numpy as np
import cv2


def draw_boxes(image: np.ndarray, boxes: List[Tuple[int, int, int, int]], color=(2, 171, 193)) -> np.ndarray:
    out = image.copy()
    bgr = (int(color[2]) if len(color) == 3 else 193, int(color[1]) if len(color) == 3 else 171, int(color[0]) if len(color) == 3 else 2)
    for x1, y1, x2, y2 in boxes:
        cv2.rectangle(out, (int(x1), int(y1)), (int(x2), int(y2)), bgr, 2)
    return out


