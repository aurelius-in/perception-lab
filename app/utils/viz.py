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


def draw_track_ids(image: np.ndarray, tracks: List[dict]) -> np.ndarray:
    out = image.copy()
    for t in tracks:
        x1, y1 = int(t.get("x1", 0)), int(t.get("y1", 0))
        tid = str(t.get("id", "?"))
        cv2.putText(out, f"ID {tid}", (x1, max(0, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        trail = t.get("trail") or []
        for i in range(1, len(trail)):
            x_prev, y_prev = trail[i - 1]
            x_cur, y_cur = trail[i]
            cv2.line(out, (int(x_prev), int(y_prev)), (int(x_cur), int(y_cur)), (0, 255, 255), 1)
    return out


def overlay_soft_masks(image: np.ndarray, masks: List[np.ndarray], color=(2, 171, 193), alpha: float = 0.35) -> np.ndarray:
    out = image.copy()
    overlay = image.copy()
    bgr = (int(color[2]), int(color[1]), int(color[0]))
    for m in masks:
        overlay[m > 0] = bgr
    return cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0)


def draw_ocr_labels(image: np.ndarray, ocr_items: List[dict]) -> np.ndarray:
    out = image.copy()
    for o in ocr_items:
        box = o.get("box") or []
        if len(box) == 4:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(out, (x1, y1), (x2, y2), (0, 200, 120), 1)
            text = str(o.get("text", ""))
            if text:
                cv2.putText(out, text, (x1, max(0, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 120), 1, cv2.LINE_AA)
    return out


