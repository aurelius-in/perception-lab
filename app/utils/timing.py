from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Dict


class StageTimer:
    def __init__(self) -> None:
        self._starts: Dict[str, float] = {}
        self.timings_ms: Dict[str, float] = {}

    def start(self, name: str) -> None:
        self._starts[name] = time.perf_counter()

    def stop(self, name: str) -> None:
        start = self._starts.pop(name, None)
        if start is None:
            return
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.timings_ms[name] = self.timings_ms.get(name, 0.0) + elapsed_ms


@contextmanager
def timed(timer: StageTimer, name: str):
    timer.start(name)
    try:
        yield
    finally:
        timer.stop(name)


