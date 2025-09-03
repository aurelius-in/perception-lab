from __future__ import annotations

import datetime as dt
import os
from pathlib import Path


class RunRegistry:
    def __init__(self, base_dir: str | os.PathLike | None = None) -> None:
        self.base = Path(base_dir or Path.cwd() / "runs")
        self.base.mkdir(parents=True, exist_ok=True)

    def new_run_id(self) -> str:
        ts = dt.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        return ts

    def ensure_run(self, run_id: str | None = None) -> str:
        rid = run_id or self.new_run_id()
        (self.base / rid).mkdir(parents=True, exist_ok=True)
        (self.base / rid / "plots").mkdir(parents=True, exist_ok=True)
        return rid


