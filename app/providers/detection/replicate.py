from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List

import requests


@dataclass
class Detection:
    x1: float
    y1: float
    x2: float
    y2: float
    score: float
    cls: str


class ReplicateDetector:
    """Minimal client wrapper. Replace with official SDK if desired."""

    def __init__(self, model: str) -> None:
        self.model = model
        self.token = os.getenv("REPLICATE_API_TOKEN", "")

    def infer(self, image_b64: str) -> List[Detection]:
        # Stub: do not call network in skeleton. Return empty list.
        # Later, implement an API call to the selected model.
        return []


