from __future__ import annotations

from app.services.metrics import get_metrics_registry


def test_metrics_registry() -> None:
    m = get_metrics_registry()
    assert m is not None
    assert hasattr(m, "fps")
