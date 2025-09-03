from __future__ import annotations


class EvaluatorAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def evaluate(self) -> dict:
        return {"metrics": {"det": {"map50": 0.0}}}


