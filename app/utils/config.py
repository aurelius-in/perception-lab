from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def load_providers_config(path: str | Path = None) -> Dict[str, Any]:
    cfg_path = Path(path) if path else Path(__file__).resolve().parents[1] / "configs" / "providers.yaml"
    if not cfg_path.exists():
        return {}
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}


