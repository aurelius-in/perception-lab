from __future__ import annotations


class RunnerAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def run(self) -> dict:
        return {"status": "ok"}


