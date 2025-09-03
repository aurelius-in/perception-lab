from __future__ import annotations

import sys
from pathlib import Path

from app.services.report import build_pdf_report


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_id:
        print("Usage: python scripts/generate_report.py <run_id>")
        sys.exit(1)
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = build_pdf_report(run_dir)
    print(str(path))


if __name__ == "__main__":
    main()


