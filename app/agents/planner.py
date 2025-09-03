from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunPlan:
    dataset: str
    profile: str
    adapters: dict


class PlannerAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def plan(self) -> RunPlan:
        return RunPlan(dataset="data/labels/demo_annotations.json", profile="realtime", adapters={})


