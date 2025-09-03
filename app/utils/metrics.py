from __future__ import annotations

from typing import List, Tuple


def iou_xyxy(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    iw = max(0.0, inter_x2 - inter_x1)
    ih = max(0.0, inter_y2 - inter_y1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    a_area = max(0.0, (ax2 - ax1)) * max(0.0, (ay2 - ay1))
    b_area = max(0.0, (bx2 - bx1)) * max(0.0, (by2 - by1))
    union = a_area + b_area - inter
    return inter / union if union > 0 else 0.0


def map50_placeholder(pred: List[Tuple[float, float, float, float]], gt: List[Tuple[float, float, float, float]]) -> float:
    # Very rough placeholder: fraction of gt matched by IoU>=0.5
    matched = 0
    used = [False] * len(pred)
    for g in gt:
        best_iou = 0.0
        best_idx = -1
        for i, p in enumerate(pred):
            if used[i]:
                continue
            iou = iou_xyxy(p, g)
            if iou >= 0.5 and iou > best_iou:
                best_iou = iou
                best_idx = i
        if best_idx >= 0:
            used[best_idx] = True
            matched += 1
    return matched / max(1, len(gt))


