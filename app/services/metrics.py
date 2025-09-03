from __future__ import annotations

from dataclasses import dataclass

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Histogram, Gauge, generate_latest


@dataclass
class MetricsRegistry:
    registry: CollectorRegistry
    latency_pre_ms: Histogram
    latency_model_ms: Histogram
    latency_post_ms: Histogram
    fps: Gauge

    def export_prometheus_text(self) -> tuple[str, str]:
        return generate_latest(self.registry).decode("utf-8"), CONTENT_TYPE_LATEST


_singleton: MetricsRegistry | None = None


def get_metrics_registry() -> MetricsRegistry:
    global _singleton
    if _singleton is not None:
        return _singleton

    reg = CollectorRegistry()
    latency_pre_ms = Histogram("latency_pre_ms", "Pre-processing latency", registry=reg, buckets=(1, 5, 10, 25, 50, 100, 250, 500))
    latency_model_ms = Histogram("latency_model_ms", "Model latency", registry=reg, buckets=(1, 5, 10, 25, 50, 100, 250, 500))
    latency_post_ms = Histogram("latency_post_ms", "Post-processing latency", registry=reg, buckets=(1, 5, 10, 25, 50, 100, 250, 500))
    fps = Gauge("fps", "Frames per second", registry=reg)

    _singleton = MetricsRegistry(
        registry=reg,
        latency_pre_ms=latency_pre_ms,
        latency_model_ms=latency_model_ms,
        latency_post_ms=latency_post_ms,
        fps=fps,
    )
    return _singleton


