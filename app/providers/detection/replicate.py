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
        if not self.token:
            return []
        # Minimal call sketch; replace with actual Replicate model endpoint as needed
        # This is intentionally conservative to avoid failures if unset
        try:
            headers = {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}
            # Pseudo endpoint; adapt per your model provider
            url = "https://api.replicate.com/v1/predictions"
            payload: Dict[str, Any] = {
                "version": self.model,
                "input": {"image": image_b64}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code >= 400:
                return []
            data = resp.json()
            # The output parsing is model-specific; return empty if unknown
            outputs = data.get("output") or []
            dets: List[Detection] = []
            for o in outputs:
                try:
                    dets.append(Detection(
                        x1=float(o.get("x1", 0)), y1=float(o.get("y1", 0)),
                        x2=float(o.get("x2", 0)), y2=float(o.get("y2", 0)),
                        score=float(o.get("score", 0)), cls=str(o.get("class", "object"))
                    ))
                except Exception:
                    continue
            return dets
        except Exception:
            return []


