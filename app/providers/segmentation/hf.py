from __future__ import annotations

from typing import List


class HfSegmentation:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def infer(self, image_b64: str) -> List[dict]:
        # Placeholder; integrate with HF segmentation endpoint
        # Return list of masks as polygons or RLE metadata
        return []


