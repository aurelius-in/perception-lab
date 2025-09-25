from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def write_report(out_dir: str | Path, metrics: Dict[str, Any]) -> Path:
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    (p / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (p / "README.txt").write_text(
        f"PerceptionLab eval report\nGenerated: {datetime.utcnow().isoformat()}Z\n",
        encoding="utf-8",
    )
    return p

