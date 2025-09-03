from __future__ import annotations

from typing import List


class ReplicatePaddleOcr:
    def __init__(self, version: str) -> None:
        self.version = version

    def infer(self, image_b64: str) -> List[dict]:
        # Placeholder; integrate with a PaddleOCR model on Replicate
        return []


