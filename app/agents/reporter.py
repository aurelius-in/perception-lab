from __future__ import annotations

from pathlib import Path

from app.services.report import build_pdf_report


class ReportAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def build(self, run_id: str) -> str:
        run_dir = Path("runs") / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = build_pdf_report(run_dir)
        return str(path)


