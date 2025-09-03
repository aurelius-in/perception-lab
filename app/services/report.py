from __future__ import annotations

from pathlib import Path


def build_pdf_report(run_dir: Path) -> Path:
    # Stub: just create an empty placeholder file
    report_path = run_dir / "report.pdf"
    report_path.write_bytes(b"%PDF-1.4\n% placeholder report\n")
    return report_path


