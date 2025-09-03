from __future__ import annotations


class DataCuratorAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def curate(self) -> dict:
        return {"manifest": {"clips": ["data/samples/day.mp4", "data/samples/night.mp4"]}}


