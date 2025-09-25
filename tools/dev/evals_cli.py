from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from evals.harness.runners.detection import run_detection_eval
from evals.harness.runners.ocr import run_ocr_eval
from evals.harness.runners.tracking import run_tracking_eval
from evals.harness.report import write_report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="evals/harness/eval_sets", help="Path to eval sets directory")
    ap.add_argument("--out", default=None, help="Output report directory (default: evals/reports/YYYYMMDD)")
    args = ap.parse_args()

    sets_dir = Path(args.sets)
    out_dir = (
        Path(args.out)
        if args.out
        else Path("evals/reports") / datetime.utcnow().strftime("%Y%m%d")
    )

    metrics = {
        "detection": run_detection_eval(sets_dir / "coco.json"),
        "ocr": run_ocr_eval(sets_dir / "ocr.json"),
        "tracking": run_tracking_eval(sets_dir / "tracking.json"),
    }
    write_report(out_dir, metrics)
    print(json.dumps({"out": str(out_dir), "metrics": metrics}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


