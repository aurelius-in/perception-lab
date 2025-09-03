from __future__ import annotations

import datetime as dt
import os
from pathlib import Path


class RunRegistry:
    def __init__(self, base_dir: str | os.PathLike | None = None) -> None:
        self.base = Path(base_dir or Path.cwd() / "runs")
        self.base.mkdir(parents=True, exist_ok=True)
        self._last_run_id: str | None = None

    def new_run_id(self) -> str:
        ts = dt.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        return ts

    def ensure_run(self, run_id: str | None = None) -> str:
        rid = run_id or self.new_run_id()
        (self.base / rid).mkdir(parents=True, exist_ok=True)
        (self.base / rid / "plots").mkdir(parents=True, exist_ok=True)
        (self.base / rid / "events.jsonl").touch(exist_ok=True)
        self._last_run_id = rid
        return rid

    def last_run_id(self) -> str | None:
        return self._last_run_id

    def append_event(self, run_id: str, event_json: str) -> None:
        path = self.base / run_id / "events.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(event_json.rstrip("\n") + "\n")

    def read_last_event(self, run_id: str) -> str | None:
        path = self.base / run_id / "events.jsonl"
        if not path.exists():
            return None
        last = None
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last = line.strip()
        return last


