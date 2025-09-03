from __future__ import annotations

from app.services.metrics import get_metrics_registry
from app.utils.metrics import iou_xyxy


def test_metrics_registry() -> None:
    m = get_metrics_registry()
    assert m is not None
    assert hasattr(m, "fps")


def test_iou_xyxy_basic() -> None:
    a = (0, 0, 10, 10)
    b = (5, 5, 15, 15)
    i = iou_xyxy(a, b)
    # Intersection area 25, union 175 => ~0.142857
    assert 0.14 < i < 0.15
