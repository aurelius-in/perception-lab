from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    base = Path("redteam/attacks")
    total = 0
    for name in ("injection.jsonl", "exfil.jsonl", "role_bypass.jsonl"):
        p = base / name
        if not p.exists():
            continue
        try:
            lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
            total += len(lines)
        except Exception:
            pass
    print(json.dumps({"attacks": total, "status": "ok"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

