from __future__ import annotations


class ObservabilityAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def collect(self) -> dict:
        return {"latency": {}, "fps": {}}


