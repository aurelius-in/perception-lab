from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class OcrBox:
    text: str
    box: list[float]


class GoogleVisionOcr:
    def __init__(self) -> None:
        pass

    def infer(self, image_b64: str) -> List[OcrBox]:
        # Skeleton: return empty list. Wire to GCV later using credentials.
        return []


