from __future__ import annotations


class EvaluatorAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def evaluate(self, dataset_path: str, tasks: list[str]) -> dict:
        return {"dataset": dataset_path, "tasks": tasks, "metrics": {"det": {"map50": 0.0}}}


