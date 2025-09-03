from __future__ import annotations

from typing import List


class RoboflowDetector:
    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key

    def infer(self, image_b64: str) -> List[dict]:
        # Placeholder; integrate with Roboflow Inference API
        return []


